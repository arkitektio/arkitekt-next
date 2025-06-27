from dataclasses import asdict
from typing import Dict, Any
import secrets


from arkitekt_next.bloks.services.admin import AdminService
from arkitekt_next.bloks.services.channel import ChannelService
from arkitekt_next.bloks.services.config import ConfigService
from arkitekt_next.bloks.services.db import DBService
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.livekit import LivekitService
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


@blok("live.arkitekt.lovekit", description="Stream live video and audio with Arkitekt")
class LovekitBlok:
    def __init__(self) -> None:
        self.dev = False
        self.host = "lovekit"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/arkitektio/lovekit-server"
        self.scopes = {
            "alpaka_pull": "Pull new Models",
            "alpaka_chat": "Add repositories to the database",
        }
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.image = "jhnnsrs/lovekit:nightly"

    def preflight(
        self,
        lok: LokService,
        db: DBService,
        redis: RedisService,
        s3: S3Service,
        config: ConfigService,
        livekit: LivekitService,
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

        livekit_access = livekit.get_access()

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
                "livekit": {
                    "host": livekit_access.host,
                    "port": livekit_access.port,
                    "api_key": livekit_access.api_key,
                    "api_secret": livekit_access.api_secret,
                },
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

    def get_builder(self):
        return "arkitekt.generic"

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        return [
            Option(
                subcommand="dev",
                help="Shoud we run the service in development mode (includes withrepo, mountrepo)?",
                default=self.dev,
            ),
            Option(
                subcommand="host",
                help="The name we should use for the host?",
                default=self.host,
            ),
            Option(
                subcommand="disable",
                help="Shoud we disable the service?",
                default=False,
            ),
            Option(
                subcommand="repo",
                help="Which repo should we use when building the service? Only active if build_repo or mount_repo is active",
                default=self.repo,
            ),
            Option(
                subcommand="command",
                help="Which command should we use when building the service?",
                default=self.command,
            ),
            Option(
                subcommand="mount_repo",
                help="Should we mount the repo into the container?",
                type=bool,
                default=self.mount_repo,
            ),
            Option(
                subcommand="build_repo",
                help="Should we build the container from the repo?",
                type=bool,
                default=self.build_repo,
            ),
            Option(
                subcommand="host",
                help="How should the service be named inside the docker-compose file?",
                default=self.host,
            ),
            Option(
                subcommand="secret_key",
                help="The secret key to use for the django service",
                default=self.secret_key,
            ),
            Option(
                subcommand="image",
                help="The image to use for the service",
                default=self.image,
            ),
        ]
