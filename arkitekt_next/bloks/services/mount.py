from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option, ExecutionContext, service
from blok.tree import YamlFile


@service("live.arkitekt.mount")
class MountService(Protocol):

    def register_mount(self, name: str, file: YamlFile) -> str: ...
