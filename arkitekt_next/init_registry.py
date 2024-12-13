import contextvars
from functools import wraps
from pydantic import BaseModel, Field
from herre_next import Herre
from fakts_next import Fakts
from .base_models import Manifest, Requirement
from typing import Callable, Dict, Optional, Protocol, TypeVar, overload
import importlib
import sys
import os
import traceback
import logging
import pkgutil
from typing import runtime_checkable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from arkitekt_next.apps import App
else:
    App = Any

Params = Dict[str, str]


current_init_hook_registry = contextvars.ContextVar(
    "current_init_hook_registry", default=None
)
GLOBAL_INIT_HOOK_REGISTRY = None


def get_default_init_hook_registry():
    global GLOBAL_INIT_HOOK_REGISTRY
    if GLOBAL_INIT_HOOK_REGISTRY is None:
        GLOBAL_INIT_HOOK_REGISTRY = InitHookRegisty()
    return GLOBAL_INIT_HOOK_REGISTRY


def get_current_init_hook_registry(allow_global=True):
    return current_init_hook_registry.get(get_default_init_hook_registry())


class Registration(BaseModel):
    name: str
    requirement: Requirement
    builder: Callable[[Herre, Fakts, Params], object]
    schema_loader: Callable[[str], object]


@runtime_checkable
class ArkitektService(Protocol):

    def get_service_name(self):
        pass

    def build_service(
        self, fakts: Fakts, herre: Herre, params: Params, manifest: Manifest
    ):
        pass

    def get_requirements(self):
        pass

    def get_graphql_schema(self):
        pass

    def get_turms_project(self):
        pass


class BaseArkitektService:

    def get_service_name(self):
        raise NotImplementedError("get_service_name not implemented")

    def build_service(
        self, fakts: Fakts, herre: Herre, params: Params, manifest: Manifest
    ):
        raise NotImplementedError("build_service not implemented")

    def get_requirements(self):
        raise NotImplementedError("get_requirements not implemented")

    def get_graphql_schema(self):
        return None

    def get_turms_project(self):
        return None


basic_requirements = [
    Requirement(
        key="lok",
        service="live.arkitekt.lok",
        description="An instance of ArkitektNext Lok to authenticate the user",
    )
]


InitHook = Callable[[App], None]


class InitHookRegisty:

    def __init__(self):
        self.init_hooks: Dict[str, InitHook] = {}

    def register(
        self,
        function: InitHook,
        name: Optional[str] = None,
        only_cli: bool = False,
    ):

        if name is None:
            name = function.__name__

        if name not in self.init_hooks:
            self.init_hooks[name] = function
        else:
            raise ValueError(f"Service {name} already registered")

    def run_all(self, app: App):
        for hook in self.init_hooks.values():
            hook(app)


T = TypeVar("T")


@overload
def init(
    function_or_actor: T,
) -> T: ...


@overload
def init(
    function_or_actor: None = None,
) -> Callable[[T], T]: ...


def init(
    *func,
    only_cli: bool = False,
    init_hook_registry: InitHookRegisty = None,
):
    """Register a function as an init hook. This function will be called when the app is initialized."""
    init_hook_registry = init_hook_registry or get_current_init_hook_registry()

    if len(func) > 1:
        raise ValueError("You can only register one function or actor at a time.")
    if len(func) == 1:
        function_or_actor = func[0]

        @wraps(function_or_actor)
        def wrapped_function(*args, **kwargs):
            return function_or_actor(*args, **kwargs)

        init_hook_registry.register(wrapped_function)

        wrapped_function.__is_init_hook__ = True

        return wrapped_function

    else:

        def real_decorator(function_or_actor):
            # Simple bypass for now
            @wraps(function_or_actor)
            def wrapped_function(*args, **kwargs):
                return function_or_actor(*args, **kwargs)

            init_hook_registry.register(wrapped_function, only_cli=only_cli)

            wrapped_function.__is_init_hook__ = True

            return wrapped_function

        return real_decorator
