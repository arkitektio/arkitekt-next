from typing import Dict, Any
import secrets


from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import Repo, YamlFile
from arkitekt_next.bloks.base import BaseArkitektService


@blok("live.arkitekt.alpaka", description="a container and app management service")
class AlpakaBlok(BaseArkitektService):
    def __init__(self) -> None:
        self.dev = False
        self.host = "alpaka"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/alpaka-server"
        self.scopes = {
            "alpaka_pull": "Pull new Models",
            "alpaka_chat": "Add repositories to the database",
        }
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.image = "jhnnsrs/alpaka:next"

    def get_additional_config(self):
        return {"ensured_repos": self.ensured_repos}

    def get_builder(self):
        return "arkitekt.generic"

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_additional_options(self):
        with_repos = Option(
            subcommand="repos",
            help="The default repos to enable for the service",
            default=self.secret_key,
        )

        return [
            with_repos,
        ]
