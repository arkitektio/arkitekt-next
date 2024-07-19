import click

from blok import blok, InitContext, ExecutionContext, CLIOption
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Optional
import secrets
from blok import blok, InitContext


class S3Credentials(BaseModel):
    access_key: str
    buckets: Dict[str, str]
    host: str
    port: int
    secret_key: str
    protocol: str
    dependency: Optional[str] = None


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


@blok("live.arkitekt.s3")
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

    def get_identifier(self):
        return "live.arkitekt.s3"

    def get_dependencies(self):
        return ["live.arkitekt.config", "live.arkitekt.gateway"]

    def retrieve_credentials(self, buckets: list[str]) -> S3Credentials:
        new_access_key = self.preformed_access_keys.pop()
        new_secret_key = self.preformed_secret_keys.pop()

        bucket_map = {}

        for bucket in buckets:
            bucket_map[bucket] = self.preformed_bucket_names.pop()

        self.buckets.extend(bucket_map.values())

        creds = S3Credentials(
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

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.preformed_bucket_names = list(
            init.kwargs.get("preformed_bucket_names", [])
        )
        self.preformed_access_keys = list(init.kwargs.get("preformed_access_keys", []))
        self.preformed_secret_keys = list(init.kwargs.get("preformed_secret_keys", []))

        init.dependencies["live.arkitekt.gateway"].expose_default(9000, self.host)

        self.config_path = init.dependencies["live.arkitekt.config"].get_path(
            self.host + ".yaml"
        )

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
                "MINIO_HOST": f"{self.host}:9000",
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
            *self.config_path.split("/"), YamlFile(**{"buckets": list(self.buckets)})
        )

    def get_options(self):
        with_host = CLIOption(
            subcommand="host",
            help="The fakts url for connection",
            default=self.host,
        )
        with_username = CLIOption(
            subcommand="username",
            help="The fakts url for connection",
            default=self.username,
        )
        with_password = CLIOption(
            subcommand="password",
            help="The fakts url for connection",
            default=self.password,
        )
        with_preformed_bucket_names = CLIOption(
            subcommand="preformed_bucket_names",
            help="The fakts url for connection",
            multiple=True,
            default=self.preformed_bucket_names,
        )
        with_preformed_acces_key = CLIOption(
            subcommand="preformed_access_keys",
            help="The fakts url for connection",
            multiple=True,
            default=self.preformed_access_keys,
        )
        with_preformed_secret_keys = CLIOption(
            subcommand="preformed_secret_keys",
            help="The fakts url for connection",
            multiple=True,
            default=self.preformed_secret_keys,
        )

        return [
            with_host,
            with_password,
            with_username,
            with_preformed_bucket_names,
            with_preformed_acces_key,
            with_preformed_secret_keys,
        ]
