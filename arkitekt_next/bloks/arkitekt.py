from pydantic import BaseModel
from typing import Dict, Any
from arkitekt_next.bloks.tailscale import TailscaleBlok
from blok import blok, InitContext, Renderer, Panel
from .livekit import LocalLiveKitBlok
from .mikro import MikroBlok
from .kabinet import KabinetBlok
from .rekuest import RekuestBlok
from .fluss import FlussBlok
from .gateway import GatewayBlok
from .internal_docker import InternalDockerBlok


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok("live.arkitekt")
class ArkitektBlok:

    def entry(self, renderer: Renderer):
        renderer.render(
            Panel(
                f"This is the arkitekt build that allows you to setup a full stack arkitekt application. Make sure to understand how bloks work before proceeding.",
                expand=False,
                title="Welcome to Arkitekt!",
                style="bold magenta",
            )
        )

    def preflight(self, lok: LocalLiveKitBlok, mikro: MikroBlok, kabinet: KabinetBlok, rekuest: RekuestBlok, fluss: FlussBlok, gateway: GatewayBlok, internal_engine: InternalDockerBlok, scale: TailscaleBlok):
        print (lok, mikro, kabinet, rekuest, fluss, gateway, internal_engine)


    def build(self, cwd):
        pass

