from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class LokCredentials:
    issuer: str
    key_type: str
    public_key: str


@service("live.arkitekt.lok")
class LokService(Protocol):
    def retrieve_credentials(self) -> LokCredentials: ...

    def retrieve_labels(self, service_name: str, builder_name: str) -> list[str]: ...

    def register_scopes(self, scopes_dict: Dict[str, str]): ...
