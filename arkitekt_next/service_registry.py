from pydantic import BaseModel, Field
from herre_next import Herre
from fakts_next import Fakts
from .base_models import Manifest, Requirement
from typing import Callable, Dict, Protocol
import importlib
import sys
import os
import traceback
import logging
import pkgutil
from typing import runtime_checkable

Params = Dict[str, str]


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
    def __init__(self):
        self.service_builders: Dict[str, ArkitektService] = {}

    def register(
        self,
        service: ArkitektService,
    ):

        name = service.get_service_name()

        if name not in self.service_builders:
            self.service_builders[name] = service
        else:
            raise ValueError(f"Service {name} already registered")

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

        sorted_requirements = sorted(requirements, key=lambda x: x.key)

        return sorted_requirements


class SetupInfo:
    services: Dict[str, object]


import os
import importlib.util
import pkgutil
import traceback
import logging


def check_and_import_services() -> ServiceBuilderRegistry:
    service_builder_registry = ServiceBuilderRegistry()
    processed_modules = set()  # Track modules that have already been processed

    # Function to load and call init_extensions from __rekuest__.py
    def load_and_call_init_extensions(module_name, rekuest_path):
        if module_name in processed_modules:
            return  # Skip if module has already been processed
        try:
            spec = importlib.util.spec_from_file_location(
                f"{module_name}.__arkitekt__", rekuest_path
            )
            rekuest_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rekuest_module)
            if hasattr(rekuest_module, "build_services"):
                for service in rekuest_module.build_services():
                    try:
                        service_builder_registry.register(service)
                    except ValueError as e:
                        print(
                            f"Failed to register service {service}: Another service with the same name is already registered {service_builder_registry.service_builders}"
                        )
                logging.info(f"Called build_services function from {module_name}")
            else:
                print(
                    f"Discovered Arkitekt-like module (containing __arkitekt__) that doesn't conform with the __arkitekt__ spec. No build_services function in {module_name}.__arkitekt__"
                )
            processed_modules.add(module_name)  # Mark this module as processed
        except Exception as e:
            print(f"Failed to call init_services for {module_name}: {e}")
            traceback.print_exc()

    # Check local modules in the current working directory
    current_directory = os.getcwd()
    for item in os.listdir(current_directory):
        item_path = os.path.join(current_directory, item)
        if os.path.isdir(item_path) and os.path.isfile(
            os.path.join(item_path, "__init__.py")
        ):
            rekuest_path = os.path.join(item_path, "__arkitekt__.py")
            if os.path.isfile(rekuest_path):
                load_and_call_init_extensions(item, rekuest_path)

    # Check installed packages
    for _, module_name, _ in pkgutil.iter_modules():
        try:
            module_spec = importlib.util.find_spec(module_name)
            if module_spec and module_spec.origin:
                rekuest_path = os.path.join(
                    os.path.dirname(module_spec.origin), "__arkitekt__.py"
                )
                if os.path.isfile(rekuest_path):
                    load_and_call_init_extensions(module_name, rekuest_path)
        except Exception as e:
            print(
                f"Failed to call init_extensions for installed package {module_name}: {e}"
            )
            traceback.print_exc()

    return service_builder_registry
