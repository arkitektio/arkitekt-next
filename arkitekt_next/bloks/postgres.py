from typing import Any, Dict, Optional

from arkitekt_next.bloks.services.db import DBService, DBCredentials
from arkitekt_next.bloks.services.mount import MountService
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
import pydantic
import namegenerator
import secrets
from blok import blok, InitContext


@blok(
    DBService,
    description="Postgres with Apache AGE",
)
class PostgresBlok(BaseModel):
    host: str = "db"
    port: int = 5432
    skip: bool = False
    password: str = pydantic.Field(default_factory=lambda: secrets.token_hex(16))
    user: str = pydantic.Field(default_factory=lambda: namegenerator.gen(separator=""))
    image: str = "jhnnsrs/daten:next"
    mount_repo: bool = False
    build_repo: bool = False
    repo: str = "https://github.com/arkitektio/daten-server"
    dev: bool = False

    registered_dbs: dict[str, DBCredentials] = {}
    build_image: Optional[Dict[str, Any]] = None

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

    def preflight(self, init: InitContext, mount: MountService):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.build_image = {
            "environment": {
                "POSTGRES_USER": self.user,
                "POSTGRES_PASSWORD": self.password,
                "POSTGRES_MULTIPLE_DATABASES": "",
            },
            "labels": ["fakts.service=live.arkitekt.postgres"],
        }

        if self.build_repo or self.dev:
            mount = init.get_service(MountService).register_mount(
                self.host, Repo(self.repo)
            )
            self.build_image["build"] = mount
        else:
            self.build_image["image"] = self.image

    def build(self, context: ExecutionContext):

        self.build_image["environment"]["POSTGRES_MULTIPLE_DATABASES"] = ",".join(
            self.registered_dbs.keys()
        )

        context.docker_compose.set_nested(f"services", self.host, self.build_image)

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
        with_repo = Option(
            subcommand="repo",
            help="The repo to use for the service",
            default=self.repo,
        )
        build_repo = Option(
            subcommand="build_repo",
            help="Should we build the repo?",
            default=self.build_repo,
        )

        mount_repo = Option(
            subcommand="mount_repo",
            help="Should we mount the repo?",
            default=self.mount_repo,
        )

        dev = Option(
            subcommand="dev",
            help="Should we run the service in development mode (includes withrepo, mountrepo)?",
            default=self.dev,
        )

        return [
            with_postgres_password,
            skip_build,
            with_user_password,
            with_image,
            with_repo,
            build_repo,
            mount_repo,
            dev,
        ]
