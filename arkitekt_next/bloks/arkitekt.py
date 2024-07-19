from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Renderer, Panel


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok("live.arkitekt")
class ArkitektBlok:
    def __init__(self) -> None:
        pass

    def get_dependencies(self):
        return [
            "live.arkitekt.lok",
            "live.arkitekt.mikro",
            "live.arkitekt.kabinet",
            "live.arkitekt.rekuest",
            "live.arkitekt.fluss",
            "live.arkitekt.gateway",
            "live.arkitekt.internal_engine",
            "io.livekit.livekit",
        ]

    def entry(self, renderer: Renderer):
        renderer.render(
            Panel(
                f"This is the arkitekt build that allows you to setup a full stack arkitekt application. Make sure to understand how bloks work before proceeding.",
                expand=False,
                title="Welcome to Arkitekt!",
                style="bold magenta",
            )
        )

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, cwd):
        pass

    def retrieve(self):
        return AdminCredentials(
            password=self.password,
            username=self.username,
            email=self.email,
        )

    def get_options(self):
        return []
