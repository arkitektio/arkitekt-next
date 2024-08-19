import click

from arkitekt_next.bloks.services.redis import RedisService, RedisConnection
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Any, Optional

from blok import blok, InitContext


@blok(
    RedisService,
    description="Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker",
)
class RedisBlok:
    def __init__(self) -> None:
        self.host = "redis"
        self.port = 6379
        self.skip = False
        self.image = "redis"

    def get_identifier(self):
        return "live.arkitekt.redis"

    def get_dependencies(self):
        return []

    def register(self) -> RedisConnection:
        return RedisConnection(
            host=self.host,
            port=self.port,
            dependency=self.host if not self.skip else None,
        )

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, context: ExecutionContext):
        redis_service = {
            "environment": {
                "REDIS_HOST": self.host,
                "REDIS_PORT": self.port,
            },
            "image": self.image,
            "ports": [f"{self.port}:{self.port}"],
        }

        context.docker_compose.set_nested(f"services", self.host, redis_service)

    def get_options(self):
        with_port = Option(
            subcommand="port",
            help="Which port to use",
            type=int,
            default=self.port,
            show_default=True,
        )
        with_host = Option(
            subcommand="host",
            help="Which public hosts to use",
            type=str,
            default=self.host,
            show_default=True,
        )
        with_skip = Option(
            subcommand="skip",
            help="Skip docker creation (if using external redis?)",
            type=bool,
            default=self.skip,
        )
        with_image = Option(
            subcommand="image",
            help="The image to use for the service",
            default=self.image,
        )

        return [with_port, with_host, with_skip, with_image]
