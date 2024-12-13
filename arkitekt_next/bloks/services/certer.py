from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol

from blok import blok, InitContext, service


@service("live.arkitekt.certer", description="Generate HTTPS certificates for services")
class CerterService(Protocol):

    def retrieve_certs_mount(self) -> str: ...

    def retrieve_depends_on(self) -> list[str]: ...
