from blok import blok, InitContext, Option
from blok.tree import YamlFile, Repo
from typing import Any, Optional, Protocol
from blok.utils import check_protocol_compliance
from dataclasses import asdict
from arkitekt_next.bloks.services import (
    GatewayService,
    DBService,
    RedisService,
    S3Service,
    ConfigService,
    MountService,
    AdminService,
    SecretService,
    LokService,
)

from blok.bloks.services.dns import DnsService


class DefaultService(Protocol):
    dev: bool
    repo: str
    command: str
    service_name: str
    host: str
    buckets: list[str]
    scopes: dict[str, str]
    secret_key: str
    mount_repo: bool
    build_repo: bool

    def get_blok_meta(self) -> str: ...

    def get_builder(self) -> str: ...


def create_default_service_dependencies():
    return [
        DnsService,
        GatewayService,
        DBService,
        RedisService,
        S3Service,
        ConfigService,
        MountService,
        AdminService,
        SecretService,
        LokService,
    ]


class BaseArkitektService:
    def get_additional_config(self):
        return {}

    def preflight(
        self,
        init: InitContext,
        lok: LokService,
        db: DBService,
        redis: RedisService,
        s3: S3Service,
        config: ConfigService,
        mount: MountService,
        admin: AdminService,
        secret: SecretService,
        gateway: Optional[GatewayService] = None,
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
        deps = init.dependencies

        lok.register_scopes(self.scopes)

        path_name = self.host

        if gateway:
            print("Registering gateway access")
            gateway_access = gateway.expose(path_name, 80, self.host)

        postgress_access = db.register_db(self.host)
        redis_access = redis.register()
        lok_access = lok.retrieve_credentials()
        admin_access = admin.retrieve()
        minio_access = s3.create_buckets(self.buckets)
        lok_labels = lok.retrieve_labels(
            self.get_blok_meta().service_identifier, self.get_builder()
        )

        django_secret = secret.retrieve_secret()

        dns_result = dns.get_dns_result()

        csrf_trusted_origins = []
        for hostname in dns_result.hostnames:
            csrf_trusted_origins.append(f"http://{hostname}")
            csrf_trusted_origins.append(f"https://{hostname}")

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

        config_mount = init.get_service(ConfigService).register_config(
            f"{self.host}.yaml", configuration
        )

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
            mount = init.get_service(MountService).register_mount(self.host, Repo(repo))
            service["volumes"].extend([f"{mount}:/workspace"])

        if build_repo or dev:
            mount = init.get_service(MountService).register_mount(self.host, Repo(repo))
            service["build"] = mount
        else:
            service["image"] = image

        service["command"] = command

        self.service = service

    def get_additional_options(self):
        return []

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
            *self.get_additional_options(),
        ]
