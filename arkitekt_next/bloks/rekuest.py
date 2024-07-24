from typing import Dict, Any
import secrets

from arkitekt_next.bloks.funcs import (
    build_default_service_options,
    create_default_service_dependencies,
    create_default_service_yaml,
)
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import Repo, YamlFile


@blok("live.arkitekt.rekuest")
class RekuestBlok:
    def __init__(self) -> None:
        self.dev = False
        self.host = "rekuest"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/rekuest-server-next"
        self.scopes = {
            "rekuest_agent": "Act as an agent",
            "rekuest_call": "Call other apps with rekuest",
        }
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos = []
        self.image = "jhnnsrs/rekuest:next"

    def get_dependencies(self):
        return create_default_service_dependencies()

    def get_builder(self):
        return "arkitekt.rekuest"

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.service = create_default_service_yaml(init, self)

        self.initialized = True

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        def_options = build_default_service_options(self)

        return [
            *def_options,
        ]
