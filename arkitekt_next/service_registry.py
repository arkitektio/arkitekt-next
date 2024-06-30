from pydantic import BaseModel, Field
from herre import Herre
from fakts import Fakts
from .model import Requirement
from typing import Callable, Dict


Params = Dict[str, str]


class Registration(BaseModel):
    name: str
    requirement: Requirement
    builder: Callable[[Herre, Fakts, Params], object]


basic_requirements = {
    "lok": Requirement(
            service="live.arkitekt.lok",
            description="An instance of ArkitektNext Lok to authenticate the user",
        ),
}


class ServiceBuilderRegistry:
    def __init__(self):
        self.service_builders = {}
        self.requirements = basic_requirements

    def register(self, name: str, service_builder: Callable[[Herre, Fakts], object], requirement: Requirement):
        self.service_builders[name] = service_builder
        self.requirements[name] = requirement

    def get(self, name):
        return self.services.get(name)
    

    def build_service_map(self, fakts: Fakts, herre: Herre, params: Params):
        return {name: builder(fakts, herre, params) for name, builder in self.service_builders.items()}
    
    def get_requirements(self):
        return self.requirements
    


service_builder_registry = ServiceBuilderRegistry()


def get_default_service_builder_registry():
    return service_builder_registry 
    
