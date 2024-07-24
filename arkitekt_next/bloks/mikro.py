import click
from pydantic import BaseModel
from typing import Dict, Any
import yaml
import secrets
from blok import blok, InitContext

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from arkitekt_next.bloks.funcs import (
    build_default_service_options,
    create_default_service_dependencies,
    create_default_service_yaml,
    DefaultService,
)


class AccessCredentials(BaseModel):
    password: str
    username: str
    host: str
    port: str
    db_name: str


@blok("live.arkitekt.mikro")
class MikroBlok:
    def __init__(self) -> None:
        self.dev = False
        self.host = "mikro"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/arkitektio/mikro-server-next"
        self.scopes = {
            "mikro_read": "Read image from the database",
            "mikro_write": "Write image to the database",
        }
        self.image = "jhnnsrs/mikro:next"
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media", "zarr", "parquet"]
        self.secret_key = secrets.token_hex(16)

    def get_dependencies(self):
        return create_default_service_dependencies()

    def get_builder(self):
        return "arkitekt.generic"

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
