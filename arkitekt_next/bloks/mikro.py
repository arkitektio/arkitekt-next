import click
from pydantic import BaseModel
from typing import Dict, Any
import yaml
import secrets
from blok import blok, InitContext

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from arkitekt_next.bloks.funcs import create_default_service_yaml


class AccessCredentials(BaseModel):
    password: str
    username: str
    host: str
    port: str
    db_name: str


@blok("live.arkitekt.mikro")
class MikroBlok:
    def __init__(self) -> None:
        self.host = "mikro"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/mikro-server-next"
        self.scopes = {"read_image": "Read image from the database"}
        self.image = "jhnnsrs/mikro:next"
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media", "zarr", "parquet"]
        self.secret_key = secrets.token_hex(16)

    def get_dependencies(self):
        return [
            "live.arkitekt.mount",
            "live.arkitekt.config",
            "live.arkitekt.gateway",
            "live.arkitekt.postgres",
            "live.arkitekt.lok",
            "live.arkitekt.admin",
            "live.arkitekt.redis",
            "live.arkitekt.s3",
        ]

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.service = create_default_service_yaml(init, self)

        self.initialized = True

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        with_repo = Option(
            subcommand="with_repo",
            help="The fakts url for connection",
            default=self.repo,
        )
        with_command = Option(
            subcommand="command",
            help="The fakts url for connection",
            default=self.command,
        )
        mount_repo = Option(
            subcommand="mount_repo",
            help="The fakts url for connection",
            is_flag=True,
            default=self.mount_repo,
        )
        build_repo = Option(
            subcommand="build_repo",
            help="The fakts url for connection",
            is_flag=True,
            default=self.build_repo,
        )
        with_host = Option(
            subcommand="host",
            help="The fakts url for connection",
            default=self.host,
        )
        with_secret_key = Option(
            subcommand="secret_key",
            help="The fakts url for connection",
            default=self.secret_key,
        )

        return [
            with_repo,
            mount_repo,
            build_repo,
            with_host,
            with_command,
            with_secret_key,
        ]
