from dataclasses import asdict
from typing import Dict, Any
import secrets


from arkitekt_next.bloks.services.admin import AdminService
from arkitekt_next.bloks.services.channel import ChannelService
from arkitekt_next.bloks.services.config import ConfigService
from arkitekt_next.bloks.services.db import DBService
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.lok import LokService
from arkitekt_next.bloks.services.mount import MountService
from arkitekt_next.bloks.services.ollama import OllamaService
from arkitekt_next.bloks.services.redis import RedisService
from arkitekt_next.bloks.services.s3 import S3Service
from arkitekt_next.bloks.services.secret import SecretService
from blok import blok, InitContext, ExecutionContext, Option
from blok.bloks.services.dns import DnsService
from blok.tree import Repo, YamlFile
from arkitekt_next.bloks.base import BaseArkitektService


@blok("live.arkitekt.alpaka", description="a container and app management service")
class AlpakaBlok(BaseArkitektService):
    def get_builder(self):
        return "arkitekt.generic"

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

    def preflight(
        self,
        lok: LokService,
        db: DBService,
        redis: RedisService,
        s3: S3Service,
        config: ConfigService,
        ollama: OllamaService,
        mount: MountService,
        admin: AdminService,
        secret: SecretService,
        gateway: GatewayService,
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
        lok.register_scopes(self.scopes)

        path_name = self.host

        gateway.expose(path_name, 80, self.host)

        postgress_access = db.register_db(self.host)
        redis_access = redis.register()
        lok_access = lok.retrieve_credentials()
        admin_access = admin.retrieve()
        minio_access = s3.create_buckets(self.buckets)
        lok_labels = lok.retrieve_labels("live.arkitekt.alpaka", self.get_builder())
        ollama_access = ollama.get_access()

        django_secret = secret.retrieve_secret()

        csrf_trusted_origins = []

        configuration = YamlFile(
            **{
                "db": asdict(postgress_access),
                "django": {
                    "admin": asdict(admin_access),
                    "debug": True,
                    "hosts": ["*"],
                    "secret_key": django_secret,
                },
                "redis": asdict(redis_access),
                "lok": asdict(lok_access),
                "s3": asdict(minio_access),
                "scopes": self.scopes,
                "force_script_name": path_name,
                "csrf_trusted_origins": csrf_trusted_origins,
                **self.get_additional_config(),
            }
        )

        config_mount = config.register_config(f"{self.host}.yaml", configuration)

        depends_on = []

        if redis_access.dependency:
            depends_on.append(redis_access.dependency)

        if postgress_access.dependency:
            depends_on.append(postgress_access.dependency)

        if minio_access.dependency:
            depends_on.append(minio_access.dependency)

        if ollama_access.dependency:
            depends_on.append(ollama_access.dependency)

        service = {
            "labels": lok_labels,
            "volumes": [f"{config_mount}:/workspace/config.yaml"],
            "depends_on": depends_on,
        }

        if mount_repo or dev:
            mount = mount.register_mount(self.host, Repo(repo))
            service["volumes"].extend([f"{mount}:/workspace"])

        if build_repo or dev:
            mount = mount.register_mount(self.host, Repo(repo))
            service["build"] = mount
        else:
            service["image"] = image

        service["command"] = command

        self.service = service
