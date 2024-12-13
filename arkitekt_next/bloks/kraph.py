import click
from pydantic import BaseModel
from typing import Dict, Any
import yaml
import secrets
from blok import blok, InitContext

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from arkitekt_next.bloks.base import BaseArkitektService


class AccessCredentials(BaseModel):
    password: str
    username: str
    host: str
    port: str
    db_name: str


@blok(
    "live.arkitekt.kraph",
    description="Kraph allows you to interconnect structures in a graph database",
)
class KraphBlok(BaseArkitektService):
    def __init__(self) -> None:
        self.dev = False
        self.host = "kraph"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/arkitektio/kraph-server"
        self.scopes = {
            "kraph_read": "Read from the graph database",
            "mikro_write": "Write image to the database",
        }
        self.image = "jhnnsrs/kraph:nightly"
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)

    def get_builder(self):
        return "arkitekt.generic"

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)
