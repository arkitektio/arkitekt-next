import click

from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from typing import Dict, Optional
from arkitekt_next.bloks.secret import SecretBlok
from arkitekt_next.bloks.services.admin import AdminService
from arkitekt_next.bloks.services.db import DBService
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.livekit import LivekitService
from arkitekt_next.bloks.services.lok import LokCredentials, LokService
import yaml
import secrets
from dataclasses import asdict

from arkitekt_next.bloks.services.redis import RedisService
from blok import blok, InitContext, ExecutionContext, Option
from blok.bloks.services.dns import DnsService
from blok.tree import YamlFile, Repo
from blok import blok, InitContext


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


# Define a custom user type that will parse and validate the user input
class UserParamType(click.ParamType):
    name = "user"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, password = value.split(":")
            return {"name": name, "password": password}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


USER = UserParamType()


# Define a custom user type that will parse and validate the user input
class GroupParamType(click.ParamType):
    name = "group"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, description = value.split(":")
            return {"name": name, "description": description}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


GROUP = GroupParamType()


class RedeemTokenParamType(click.ParamType):
    name = "redeem_token"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "user" in value, f"scope is required {value}"
            assert "token" in value, f"description is required {value}"
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


TOKEN = RedeemTokenParamType()


class ScopeParamType(click.ParamType):
    name = "scope"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "scope" in value, f"scope is required {value}"
            assert "description" in value, f"description is required {value}"
            return value

        try:
            name, description = value.split(":")
            return {"scope": name, "description": description}
        except ValueError:
            self.fail(
                f"Scopes '{value}' is not in the correct format. It should be 'scope:description'.",
                param,
                ctx,
            )


SCOPE = ScopeParamType()


@blok(LokService, description="A local sign service")
class LocalSignBlok:
    db_name: str

    def __init__(self) -> None:
        self.db_name = "lok_db"
        self.mount_repo = False
        self.build_repo = False
        self.private_key = None
        self.public_key = None
        self.host = "lok"
        self.dev = False
        self.with_repo = False
        self.users = []
        self.tokens = []
        self.groups = []
        self.scopes = {}
        self.key = None
        self.deployment_name = "default"
        self.token_expiry_seconds = 700000
        self.preformed_redeem_tokens = [secrets.token_hex(16) for i in range(80)]
        self.registered_tokens = {}
        self.local_access = None

    def retrieve_credentials(self) -> LokCredentials:
        return LokCredentials(
            public_key=self.public_key, key_type="RS256", issuer="lok"
        )

    def retrieve_labels(self, service_name: str, builder_name: str) -> list[str]:
        return [
            f"fakts.service={service_name}",
            f"fakts.builder={builder_name}",
        ]

    def retrieve_token(self, user: str = "admin") -> str:
        pass 
        return "fake-token"

    def register_scopes(self, scopes_dict: Dict[str, str]) -> LokCredentials:
        self.scopes = self.scopes | scopes_dict

    def preflight(
        self,
        init: InitContext
    ):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        assert self.public_key, "Public key is required"
        assert self.private_key, "Private key is required"


    def build(self, context: ExecutionContext):
        context.file_tree.set_nested("secrets", "public_key.pem", self.public_key)
        context.file_tree.set_nested("secrets", "private_key.pem", self.private_key)

    def get_options(self):
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=crypto_default_backend()
        )

        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption(),
        ).decode()

        public_key = (
            key.public_key()
            .public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )

        with_dev = Option(
            subcommand="dev",
            help="Run the service in development mode",
            type=bool,
            default=self.dev,
            show_default=True,
        )

        with_fakts_url = Option(
            subcommand="db_name",
            help="The name of the database",
            default="db_name",
            show_default=True,
        )
        with_users = Option(
            subcommand="users",
            help="Users that should be greated by default. Format is name:password",
            default=["admin:admin"],
            multiple=True,
            type=USER,
            show_default=True,
        )
        with_groups = Option(
            subcommand="groups",
            help="Groups that should be greated by default. Format is name:description",
            default=["admin:admin_group"],
            multiple=True,
            type=GROUP,
            show_default=True,
        )
        with_public_key = Option(
            subcommand="public_key",
            help="The public key for the JWT creation",
            default=public_key,
            required=True,
            callback=validate_public_key,
        )
        with_private_key = Option(
            subcommand="private_key",
            help="The corresponding private key for the JWT creation",
            default=private_key,
            callback=validate_private_key,
            required=True,
        )

        return [
            with_dev,
            with_fakts_url,
            with_users,
            with_groups,
            with_private_key,
            with_public_key,
        ]


def validate_public_key(ctx, param, value):
    if not value.startswith("ssh-rsa"):
        raise click.BadParameter(
            f"Public key must be in ssh-rsa format. Started with {value}"
        )
    return value


def validate_private_key(ctx, param, value):
    if not value.startswith("-----BEGIN PRIVATE KEY-----"):
        raise click.BadParameter(
            f"Private key must be in PEM format. Started with {value}"
        )
    return value
