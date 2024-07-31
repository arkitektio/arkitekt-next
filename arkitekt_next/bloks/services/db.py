from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol, Optional

from blok import blok, InitContext, service
from dataclasses import dataclass


@dataclass
class DBCredentials:
    password: str
    username: str
    host: str
    port: int
    db_name: str
    engine: str = "django.db.backends.postgresql"
    dependency: Optional[str] = None


@service("live.arkitekt.postgres")
class DBService(Protocol):
    def register_db(self, db_name: str) -> DBCredentials: ...
