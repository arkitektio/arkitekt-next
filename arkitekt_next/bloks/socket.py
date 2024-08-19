from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Option, ExecutionContext
from blok.tree import YamlFile


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok(
    "live.arkitekt.docker_socket", description="Hosting the docker socket of the host"
)
class DockerSocketBlok:
    def __init__(self) -> None:
        self.docker_socket = "/var/run/docker.sock"
        self.registered_configs = {}

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def register_socket(self, name: str) -> str:
        self.registered_configs[name] = name
        return self.docker_socket

    def build(self, ex: ExecutionContext):
        pass

    def get_options(self):
        config_path = Option(
            subcommand="docker_socket",
            help="Which docker_socket to use for configs",
            default=self.docker_socket,
            show_default=True,
        )

        return [config_path]
