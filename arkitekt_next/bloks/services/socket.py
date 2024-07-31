from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol

from blok import blok, InitContext, service


@service("live.arkitekt.docker_socket")
class DockerSocketService(Protocol):
    def register_socket(self, name: str) -> str:
        self.registered_configs[name] = name
        return self.docker_socket
