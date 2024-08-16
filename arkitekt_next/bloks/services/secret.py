from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class AdminCredentials:
    password: str
    username: str
    email: str


@service("live.arkitekt.secrets")
class SecretService(Protocol):

    def retrieve_secret() -> str:
        pass
