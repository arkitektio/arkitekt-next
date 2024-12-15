import contextvars
from functools import wraps
from pydantic import BaseModel, Field
from herre_next import Herre
from fakts_next import Fakts
from .base_models import Manifest, Requirement
from typing import Callable, Dict, Optional, Protocol, TypeVar, overload
from typing import runtime_checkable

Params = Dict[str, str]


current_service_registry = contextvars.ContextVar(
    "current_service_registry", default=None
)
GLOBAL_SERVICE_REGISTRY = None


def get_default_service_registry():
    global GLOBAL_SERVICE_REGISTRY
    if GLOBAL_SERVICE_REGISTRY is None:
        GLOBAL_SERVICE_REGISTRY = ServiceBuilderRegistry()
    return GLOBAL_SERVICE_REGISTRY


def get_current_service_registry(allow_global=True):
    return current_service_registry.get(get_default_service_registry())


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


class ServiceBuilderRegistry:
    def __init__(self, import_services=True):
        self.service_builders: Dict[str, ArkitektService] = {}
        self.additional_requirements: Dict[str, Requirement] = {}

    def register(
        self,
        service: ArkitektService,
    ):

        name = service.get_service_name()

        if name not in self.service_builders:
            self.service_builders[name] = service
        else:
            raise ValueError(f"Service {name} already registered")

    def register_requirement(self, requirement: Requirement):
        if requirement.key in self.additional_requirements:
            raise ValueError(f"Requirement {requirement.key} already registered)")
        self.additional_requirements[requirement.key] = requirement

    def get(self, name):
        return self.services.get(name)

    def build_service_map(
        self, fakts: Fakts, herre: Herre, params: Params, manifest: Manifest
    ):
        potentially_needed_services = {
            name: service.build_service(fakts, herre, params, manifest)
            for name, service in self.service_builders.items()
        }

        return {
            key: value
            for key, value in potentially_needed_services.items()
            if value is not None
        }

    def get_requirements(self):

        requirements = [
            Requirement(
                key="lok",
                service="live.arkitekt.lok",
                description="An instance of ArkitektNext Lok to authenticate the user",
            )
        ]
        taken_requirements = set()

        for service in self.service_builders.values():
            for requirement in service.get_requirements():
                if requirement.key not in taken_requirements:
                    taken_requirements.add(requirement.key)
                    requirements.append(requirement)

        for requirement in self.additional_requirements.values():
            if requirement.key not in taken_requirements:
                taken_requirements.add(requirement.key)
                requirements.append(requirement)

        sorted_requirements = sorted(requirements, key=lambda x: x.key)

        return sorted_requirements


class SetupInfo:
    services: Dict[str, object]


import os
import importlib.util
import pkgutil
import traceback
import logging

T = TypeVar("T")


@overload
def require(
    key: str,
    service: str = None,
    description: str = None,
) -> Callable[[T], T]: ...


def require(
    key: str,
    service: str = None,
    description: str = None,
    service_registry: Optional[ServiceBuilderRegistry] = None,
):
    """Register a requirement with the service registry"""
    service_hook_registry = service_registry or get_current_service_registry()

    requirement = Requirement(key=key, service=service, description=description)
    service_hook_registry.register_requirement(requirement)

    return requirement
