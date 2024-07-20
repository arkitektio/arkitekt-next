from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol

from blok import blok, InitContext, service


@blok("live.arkitekt.gateway")
class GatewayService(Protocol):

    def expose(self, path_name: str, port: int, host: str, strip_prefix: bool = True):
       ...

    def expose_default(self, port: int, host: str):
        ...

    def expose_port(self, port: int, host: str, tls: bool = False):
        ...
    