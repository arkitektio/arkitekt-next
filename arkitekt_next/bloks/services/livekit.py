from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class LivekitCredentials:
    api_key: str
    api_secret: str
    api_url: str


@service("io.livekit.livekit")
class LivekitService(Protocol):

    def retrieve_access(self) -> LivekitCredentials: ...
