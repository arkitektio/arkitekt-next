from typing import Dict, Any
import secrets


from arkitekt_next.bloks.services.admin import AdminService
from arkitekt_next.bloks.services.channel import ChannelService
from arkitekt_next.bloks.services.config import ConfigService
from arkitekt_next.bloks.services.db import DBService
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.lok import LokService
from arkitekt_next.bloks.services.mount import MountService
from arkitekt_next.bloks.services.redis import RedisService
from arkitekt_next.bloks.services.s3 import S3Service
from arkitekt_next.bloks.services.secret import SecretService
from blok import blok, InitContext, ExecutionContext, Option
from blok.bloks.services.dns import DnsService
from blok.tree import Repo, YamlFile
from arkitekt_next.bloks.base import BaseArkitektService


@blok("live.arkitekt.alpaka", description="a container and app management service")
class AlpakaBlok(BaseArkitektService):
    def __init__(self) -> None:
        self.dev = False
        self.host = "alpaka"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/arkitektio/alpaka-server"
        self.scopes = {
            "alpaka_pull": "Pull new Models",
            "alpaka_chat": "Add repositories to the database",
        }
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.image = "jhnnsrs/alpaka:nightly"

    def get_additional_config(self):
        return {"ensured_repos": self.ensured_repos}

    def preflight(
        self,
        init: InitContext,
        lok: LokService,
        db: DBService,
        redis: RedisService,
        s3: S3Service,
        config: ConfigService,
        channel: ChannelService,
        mount: MountService,
        admin: AdminService,
        secret: SecretService,
        gateway: GatewayService | None = None,
        dns: DnsService = None,
        mount_repo: bool = False,
        host: str = "",
        image: str = "",
        secret_key: str = "",
        build_repo: bool = False,
        command: str = "",
        repo: str = "",
        disable: bool = False,
        dev: bool = False,
    ):
        return super().preflight(
            init,
            lok,
            db,
            redis,
            s3,
            config,
            channel,
            mount,
            admin,
            secret,
            gateway,
            dns,
            mount_repo,
            host,
            image,
            secret_key,
            build_repo,
            command,
            repo,
            disable,
            dev,
        )

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
