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

    def retrieve(self):
        return AdminCredentials(
            password=self.password,
            username=self.username,
            email=self.email,
        )
