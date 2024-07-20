from typing import Optional

from arkitekt_next.bloks.services.db import DBService, DBCredentials
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
import pydantic
import namegenerator
import secrets
from blok import blok, InitContext




@blok(DBService)
class PostgresBlok(BaseModel):
    host: str = "db"
    port: int = 5432
    skip: bool = False
    password: str = pydantic.Field(default_factory=lambda: secrets.token_hex(16))
    user: str = pydantic.Field(default_factory=lambda: namegenerator.gen(separator=""))
    image: str = "jhnnsrs/daten:next"

    registered_dbs: dict[str, DBCredentials] = {}

    def get_dependencies(self):
        return []

    def get_identifier(self):
        return "live.arkitekt.postgres"

    def register_db(self, db_name: str) -> DBCredentials:
        if db_name in self.registered_dbs:
            return self.registered_dbs[db_name]
        else:
            access_credentials = DBCredentials(
                password=self.password,
                username=self.user,
                host=self.host,
                port=self.port,
                db_name=db_name,
                dependency=self.host if not self.skip else None,
            )
            self.registered_dbs[db_name] = access_credentials
            return access_credentials

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, context: ExecutionContext):
        db_service = {
            "environment": {
                "POSTGRES_USER": self.user,
                "POSTGRES_PASSWORD": self.password,
                "POSTGRES_MULTIPLE_DATABASES": ",".join(self.registered_dbs.keys()),
            },
            "image": self.image,
            "labels": ["fakts.service=live.arkitekt.postgres"],
        }

        context.docker_compose.set_nested(f"services", self.host, db_service)

    def get_options(self):
        with_postgres_password = Option(
            subcommand="password",
            help="The postgres password for connection",
            default=self.password,
        )
        with_user_password = Option(
            subcommand="user",
            help="The postgress user_name",
            default=self.user,
        )
        skip_build = Option(
            subcommand="skip",
            help="Should the service not be created? E.g when pointing outwards?",
            default=self.skip,
        )
        with_image = Option(
            subcommand="image",
            help="The image to use for the service",
            default=self.image,
        )

        return [with_postgres_password, skip_build, with_user_password, with_image]
