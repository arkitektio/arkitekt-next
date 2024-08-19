from typing import Dict, Any
import secrets

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import Repo, YamlFile
from arkitekt_next.bloks.base import BaseArkitektService


@blok("live.arkitekt.rekuest", description="Rekuest is the RPC and Functionaliy hub")
class RekuestBlok(BaseArkitektService):
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
        self.image = "jhnnsrs/rekuest:next"

    def get_builder(self):
        return "arkitekt.rekuest"

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)
