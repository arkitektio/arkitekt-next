from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class AdminCredentials:
    password: str
    username: str
    email: str


@service("live.arkitekt.admin")
class AdminService(Protocol):
    def retrieve(self) -> AdminCredentials:
        """Retrieve the admin credentials.

        Admin credentials should be used to access the admin interface of the application.

        """
