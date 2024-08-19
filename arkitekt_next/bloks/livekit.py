from typing import Dict, Any
import secrets

from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.livekit import LivekitService, LivekitCredentials
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo


@blok(LivekitService, description="a self-hosted livekit server")
class LocalLiveKitBlok:
    def __init__(self) -> None:
        self.host = "livekit"
        self.command = ["--dev", "--bind", "0.0.0.0"]
        self.image = "livekit/livekit-server:latest"
        self.mount_repo = True
        self.build_repo = True
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos = []
        self.port_range = [50000, 50030]
        self.api_key = "devkey"
        self.api_secret = "secret"
        self.skip = False

    def preflight(self, init: InitContext, gateway: GatewayService):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        deps = init.dependencies

        if self.skip:
            return

        gateway.expose_port(7880, self.host, True)
        gateway.expose_port_to(7882, self.host, 7880, False)

        self.initialized = True

    def retrieve_access(self):
        return LivekitCredentials(
            **{
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "api_url": f"http://{self.host}:7880",
            }
        )

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
            "ports": [
                f"{self.port_range[0]}-{self.port_range[1]}:{self.port_range[0]}-{self.port_range[1]}",
                "7881:7881",
            ],
        }

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
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
        )

        return [
            with_host,
            with_skip,
        ]

    def __str__(self) -> str:
        return (
            f"LiveKitBlok(host={self.host}, command={self.command}, image={self.image})"
        )
