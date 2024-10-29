import secrets

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from arkitekt_next.bloks.base import BaseArkitektService
from typing import List


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


@blok(
    "live.arkitekt.fluss", description="A service for managing workflows and their data"
)
class FlussBlok(BaseArkitektService):
    def __init__(self) -> None:
        self.dev = False
        self.host = "fluss"
        self.command = "bash run-debug.sh"
        self.image = "jhnnsrs/fluss_next:nightly"
        self.repo = "https://github.com/jhnnsrs/fluss-server-next"
        self.scopes = {"read_image": "Read image from the database"}
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos: List[str] = []

    def get_builder(self):
        return "arkitekt.generic"

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)
