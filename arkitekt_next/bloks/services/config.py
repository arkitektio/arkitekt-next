from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option, ExecutionContext, service
from blok.tree import YamlFile


@service("live.arkitekt.config")
class ConfigService(Protocol):

    def register_config(self, name: str, file: YamlFile) -> str: ...

    def get_path(self, name: str) -> str:
        ...
        return f"./{self.config_path}/" + name
