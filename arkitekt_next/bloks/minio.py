import click

from arkitekt_next.bloks.services.config import ConfigService
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.name import NameService
from arkitekt_next.bloks.services.secret import SecretService
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Optional
import secrets
from blok import blok, InitContext
from arkitekt_next.bloks.services.s3 import S3Credentials, S3Service


class BucketMapParamType(click.ParamType):
    name = "redeem_token"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            user, token = value.split(":")
            return {"user": user, "token": token}
        except ValueError:
            self.fail(
                f"RedeemToken '{value}' is not in the correct format. It should be 'username:token'.",
                param,
                ctx,
            )


TOKEN = BucketMapParamType()


@blok(
    S3Service,
    description="Minio is an easy use self-hosted object storage service",
)
class MinioBlok:
    db_name: str

    def __init__(self) -> None:
        self.users = []
        self.username = secrets.token_hex(16)
        self.password = secrets.token_hex(16)
        self.protocol = "http"
        self.host = "minio"
        self.port = 9000
        self.skip = False
        self.scopes = {}
        self.init_image = "jhnnsrs/init:paper"
        self.minio_image = "minio/minio:RELEASE.2023-02-10T18-48-39Z"
        self.buckets = []
        self.registered_clients = []
        self.preformed_bucket_names = [secrets.token_hex(16) for i in range(100)]
        self.preformed_access_keys = [secrets.token_hex(16) for i in range(100)]
        self.preformed_secret_keys = [secrets.token_hex(16) for i in range(100)]

    def create_buckets(self, buckets: list[str]) -> S3Credentials:
        new_access_key = self.secret_service.retrieve_secret()
        new_secret_key = self.secret_service.retrieve_secret()

        bucket_map = {}

        for bucket in buckets:
            bucket_name = self.name_service.retrieve_name()
            bucket_map[bucket] = bucket_name
            self.gateway_service.expose(bucket_name, 9000, self.host)

        self.buckets.extend(bucket_map.values())

        creds = S3Credentials(
            name=self.name_service.retrieve_name(),
            access_key=new_access_key,
            buckets=bucket_map,
            host=self.host,
            port=self.port,
            secret_key=new_secret_key,
            protocol=self.protocol,
            dependency=self.host if not self.skip else None,
        )

        self.registered_clients.append(creds)

        return creds

    def preflight(
        self,
        init: InitContext,
        secret: SecretService,
        name: NameService,
        gateway: GatewayService,
        config: ConfigService,
    ):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.secret_service = secret
        self.name_service = name
        self.gateway_service = gateway

        self.config_path = config.get_path(self.host + ".yaml")

    def build(self, context: ExecutionContext):
        minio_service_init = {
            "depends_on": {
                "minio": {
                    "condition": "service_started",
                },
            },
            "environment": {
                "MINIO_ROOT_PASSWORD": self.password,
                "MINIO_ROOT_USER": self.username,
                "MINIO_HOST": f"http://{self.host}:9000",
            },
            "image": self.init_image,
            "volumes": [f"{self.config_path}:/workspace/config.yaml"],
        }

        minio_service = {
            "command": ["server", "/data"],
            "environment": {
                "MINIO_ROOT_PASSWORD": self.password,
                "MINIO_ROOT_USER": self.username,
            },
            "image": self.minio_image,
            "volumes": ["./data:/data"],
            "labels": ["fakts.service=live.arkitekt.s3", "fakts.builder=arkitekt.s3"],
        }

        context.file_tree.set_nested("data", {})

        context.docker_compose.set_nested("services", self.host, minio_service)
        context.docker_compose.set_nested(
            "services", f"{self.host}_init", minio_service_init
        )

        context.file_tree.set_nested(
            *self.config_path.split("/"),
            YamlFile(
                buckets=[{"name": i} for i in self.buckets],
                users=[
                    {
                        "access_key": i.access_key,
                        "secret_key": i.secret_key,
                        "name": i.name,
                        "policies": ["readwrite"],
                    }
                    for i in self.registered_clients
                ],
            ),
        )

    def get_options(self):
        with_host = Option(
            subcommand="host",
            help="The fakts_next url for connection",
            default=self.host,
        )
        with_username = Option(
            subcommand="username",
            help="The fakts_next url for connection",
            default=self.username,
        )
        with_password = Option(
            subcommand="password",
            help="The fakts_next url for connection",
            default=self.password,
        )

        return [
            with_host,
            with_password,
            with_username,
        ]
