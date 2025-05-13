from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Option
from arkitekt_next.bloks.services.channel import ChannelService


@blok(ChannelService, description="The current channel of the application")
class ChannelBlok:
    def __init__(self) -> None:
        self.name = "default"

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def retrieve(self):
        return self.name

    def get_options(self):
        with_name = Option(
            subcommand="name",
            help="Which channel name to use",
            default=self.name,
            show_default=True,
        )

        return [with_name]
