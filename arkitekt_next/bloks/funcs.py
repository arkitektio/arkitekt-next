from blok import blok, InitContext, Option
from blok.tree import YamlFile, Repo
from typing import Protocol
from blok.utils import check_protocol_compliance
from dataclasses import asdict

class DefaultService(Protocol):
    service_name: str
    host: str
    buckets: list[str]
    scopes: dict[str, str]
    secret_key: str
    mount_repo: bool
    build_repo: bool

    def get_identifier(self) -> str: ...


def create_default_service_yaml(
    init: InitContext,
    self: DefaultService,
) -> YamlFile:
    check_protocol_compliance(self, DefaultService)
    deps = init.dependencies
    deps["live.arkitekt.lok"].register_scopes(self.scopes)

    gateway_access = deps["live.arkitekt.gateway"].expose(self.host, 80, self.host)

    postgress_access = deps["live.arkitekt.postgres"].register_db(self.host)
    redis_access = deps["live.arkitekt.redis"].register()
    lok_access = deps["live.arkitekt.lok"].retrieve_credentials()
    admin_access = deps["live.arkitekt.admin"].retrieve()
    minio_access = deps["live.arkitekt.s3"].create_buckets(self.buckets)
    lok_access = deps["live.arkitekt.lok"].retrieve_credentials()
    lok_labels = deps["live.arkitekt.lok"].retrieve_labels(self.get_identifier())

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
        }
    )

    config_mount = deps["live.arkitekt.config"].register_config(
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
        mount = deps["live.arkitekt.mount"].register_mount(self.host, Repo(self.repo))
        service["volumes"].extend([f"{mount}:/workspace"])

    if self.build_repo:
        mount = deps["live.arkitekt.mount"].register_mount(self.host, Repo(self.repo))
        service["build"] = mount
    else:
        service["image"] = self.image

    service["command"] = self.command

    return service
