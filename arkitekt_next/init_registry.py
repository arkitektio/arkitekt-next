import contextvars
from functools import wraps
from typing import Callable, Dict, Optional, TypeVar, overload, cast
from arkitekt_next.apps.protocols import App

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


T = TypeVar("T", bound=InitHook)


@overload
def init(
    *func: T,
) -> T: ...


@overload
def init(
    *,
    only_cli: bool = False,
    init_hook_registry: InitHookRegisty | None = None,
) -> Callable[[T], T]: ...


def init(
    *func: T,
    only_cli: bool = False,
    init_hook_registry: InitHookRegisty | None = None,
) -> T | Callable[[T], T]:
    """Register a function as an init hook. This function will be called when the app is initialized."""
    init_hook_registry = init_hook_registry or get_default_init_hook_registry()

    if len(func) > 1:
        raise ValueError("You can only register one function or actor at a time.")
    if len(func) == 1:
        function_or_actor = func[0]

        init_hook_registry.register(function_or_actor)

        setattr(function_or_actor, "__is_init_hook__", True)

        return function_or_actor

    else:

        def real_decorator(function_or_actor):
            # Simple bypass for now
            @wraps(function_or_actor)
            def wrapped_function(*args, **kwargs):
                return function_or_actor(*args, **kwargs)

            init_hook_registry.register(wrapped_function, only_cli=only_cli)

            setattr(function_or_actor, "__is_init_hook__", True)

            return wrapped_function

        return cast(Callable[[T], T], real_decorator)
