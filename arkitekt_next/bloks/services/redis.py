from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol, Optional

from blok import blok, InitContext, service
from dataclasses import dataclass


@dataclass
class RedisConnection:
    host: str
    port: int
    dependency: Optional[str] = None


@service("live.arkitekt.redis")
class RedisService(Protocol):
    def register(self) -> RedisConnection: ...
