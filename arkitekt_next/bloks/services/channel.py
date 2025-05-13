from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass



@service("live.arkitekt.channel")
class ChannelService(Protocol):

    def retrieve_channel(self) -> str:
        return str
