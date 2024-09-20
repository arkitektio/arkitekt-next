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
from .orkestrator import OrkestratorBlok
from typing import Optional


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok("live.arkitekt")
class ArkitektBlok:
    def entry(self, renderer: Renderer):
        renderer.render(
            Panel(
                f"""This is the arkitekt build that allows you to setup a full stack arkitekt application. You can use this to setup a full stack application with the following services""",
                expand=False,
                title="Welcome to Arkitekt!",
                style="bold magenta",
            )
        )

    def preflight(
        self,
        gateway: GatewayBlok,
        livekit: Optional[LocalLiveKitBlok] = None,
        mikro: Optional[MikroBlok] = None,
        kabinet: Optional[KabinetBlok] = None,
        rekuest: Optional[RekuestBlok] = None,
        fluss: Optional[FlussBlok] = None,
        internal_engine: Optional[InternalDockerBlok] = None,
        scale: Optional[TailscaleBlok] = None,
        orkestrator: Optional[OrkestratorBlok] = None,
    ):
        pass

    def build(self, cwd):
        pass
