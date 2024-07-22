from blok import blok, InitContext, Option
from blok.tree import YamlFile, Repo
from typing import Protocol
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


def create_default_service_yaml(
    init: InitContext,
    self: DefaultService,
) -> YamlFile:
    check_protocol_compliance(self, DefaultService)
    deps = init.dependencies

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

    if self.mount_repo:
        mount = init.get_service(MountService).register_mount(
            self.host, Repo(self.repo)
        )
        service["volumes"].extend([f"{mount}:/workspace"])

    if self.build_repo:
        mount = init.get_service(MountService).register_mount(
            self.host, Repo(self.repo)
        )
        service["build"] = mount
    else:
        service["image"] = self.image

    service["command"] = self.command

    return service
