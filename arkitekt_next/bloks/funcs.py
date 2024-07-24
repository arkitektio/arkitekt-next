from blok import blok, InitContext, Option
from blok.tree import YamlFile, Repo
from typing import Any, Protocol
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

    def get_identifier(self) -> str: ...

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


def build_default_service_options(self: DefaultService) -> list[Option]:
    return [
        Option(
            subcommand="dev",
            help="Shoud we run the service in development mode (includes withrepo, mountrepo)?",
            default=self.dev,
        ),
        Option(
            subcommand="disable",
            help="Shoud we disable the service?",
            default=False,
        ),
        Option(
            subcommand="with_repo",
            help="Which repo should we use when building the service? Only active if build_repo or mount_repo is active",
            default=self.repo,
        ),
        Option(
            subcommand="with_command",
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
    ]


def create_default_service_yaml(
    init: InitContext,
    self: DefaultService,
    additional_keys: dict[str, Any] = None,
) -> YamlFile:
    check_protocol_compliance(self, DefaultService)
    deps = init.dependencies
    additional_keys = additional_keys or {}

    init.get_service(LokService).register_scopes(self.scopes)

    path_name = self.host

    gateway_access = init.get_service(GatewayService).expose(path_name, 80, self.host)

    postgress_access = init.get_service(DBService).register_db(self.host)
    redis_access = init.get_service(RedisService).register()
    lok_access = init.get_service(LokService).retrieve_credentials()
    admin_access = init.get_service(AdminService).retrieve()
    minio_access = init.get_service(S3Service).create_buckets(self.buckets)
    lok_labels = init.get_service(LokService).retrieve_labels(
        self.get_identifier(), self.get_builder()
    )

    dns_result = init.get_service(DnsService).get_dns_result()

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
                "secret_key": self.secret_key,
            },
            "redis": asdict(redis_access),
            "lok": asdict(lok_access),
            "s3": asdict(minio_access),
            "scopes": self.scopes,
            "force_script_name": path_name,
            "csrf_trusted_origins": csrf_trusted_origins,
            **additional_keys,
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

    if self.mount_repo or self.dev:
        mount = init.get_service(MountService).register_mount(
            self.host, Repo(self.repo)
        )
        service["volumes"].extend([f"{mount}:/workspace"])

    if self.build_repo or self.dev:
        mount = init.get_service(MountService).register_mount(
            self.host, Repo(self.repo)
        )
        service["build"] = mount
    else:
        service["image"] = self.image

    service["command"] = self.command

    return service
