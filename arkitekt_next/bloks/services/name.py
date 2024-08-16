from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@service("live.arkitekt.names")
class NameService(Protocol):

    def retrieve_name(self) -> str:
        pass
