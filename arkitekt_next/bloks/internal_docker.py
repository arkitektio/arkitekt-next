from typing import Dict, Any
import secrets

from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo


@blok("live.arkitekt.internal_engine")
class InternalDockerBlok:
    def __init__(self) -> None:
        self.host = "internal_docker"
        self.command = (
            "arkitekt-next run prod --redeem-token=mylittletoken --url http://caddy:80"
        )
        self.image = "jhnnsrs/deployer:0.0.1-vanilla"
        self.instance_id = "INTERNAL_DOCKER"

    def get_dependencies(self):
        return ["live.arkitekt.docker_socket"]

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        deps = init.dependencies

        if self.skip:
            return

        self._socket = deps["live.arkitekt.docker_socket"].register_socket(self.host)

        self.initialized = True

    def build(self, context: ExecutionContext):
        if self.skip:
            return
        db_service = {
            "labels": [
                "fakts.service=io.livekit.livekit",
                "fakts.builder=livekitio.livekit",
            ],
            "image": self.image,
            "command": self.command,
            "volumes": [f"{self._socket}:/var/run/docker.sock"],
            "environment": {
                "INSTANCE_ID": self.instance_id,
            },
        }

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
        with_command = Option(
            subcommand="command",
            help="The fakts url for connection",
            default=self.command,
        )
        with_host = Option(
            subcommand="host",
            help="The fakts url for connection",
            default=self.host,
        )
        with_skip = Option(
            subcommand="skip",
            help="The fakts url for connection",
            default=False,
            type=bool,
            is_flag=True,
        )

        return [
            with_host,
            with_command,
            with_skip,
        ]

    def __str__(self) -> str:
        return (
            f"InterDocker(host={self.host}, command={self.command}, image={self.image})"
        )
