from typing import Dict, Any
import secrets

from arkitekt_next.bloks.funcs import (
    create_default_service_yaml,
    create_default_service_dependencies,
)
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import Repo, YamlFile


@blok("live.arkitekt.kabinet")
class KabinetBlok:
    def __init__(self) -> None:
        self.host = "kabinet"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/kabinet-server"
        self.scopes = {
            "kabinet_deploy": "Deploy containers",
            "kabinet_add_repo": "Add repositories to the database",
        }
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos = ["jhnnsrs/ome:main", "jhnnsrs/renderer:main"]
        self.image = "jhnnsrs/kabinet:next"

    def get_builder(self):
        return "arkitekt.generic"

    def get_dependencies(self):
        return create_default_service_dependencies()

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.service = create_default_service_yaml(
            init, self, {"ensured_repos": self.ensured_repos}
        )

        self.initialized = True

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        with_repo = Option(
            subcommand="with_repo",
            help="Which repo should we use when building the service? Only active if build_repo or mount_repo is active",
            default=self.repo,
        )
        with_command = Option(
            subcommand="command",
            help="Which command should be run when starting the service",
            default=self.command,
        )
        mount_repo = Option(
            subcommand="mount_repo",
            help="Should we mount the repo into the container?",
            type=bool,
            default=self.mount_repo,
        )
        build_repo = Option(
            subcommand="build_repo",
            help="Should we build the container from the repo?",
            type=bool,
            default=self.build_repo,
        )
        with_host = Option(
            subcommand="host",
            help="How should the service be named inside the docker-compose file?",
            default=self.host,
        )
        with_secret_key = Option(
            subcommand="secret_key",
            help="The secret key to use for the django service",
            default=self.secret_key,
        )
        with_repos = Option(
            subcommand="repos",
            help="The default repos to enable for the service",
            default=self.secret_key,
        )

        return [
            with_repo,
            mount_repo,
            build_repo,
            with_host,
            with_command,
            with_secret_key,
            with_repos,
        ]
