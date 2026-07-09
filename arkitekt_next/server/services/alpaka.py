"""Alpaka service - AI/ML model management.

Alpaka provides AI and machine learning model management for Arkitekt,
enabling users to deploy and use ML models through LLM integrations.
"""

from typing import ClassVar, Dict

from pydantic import Field

from arkitekt_next.server.config import (
    BucketConfig,
    DBConfig,
    LocalBucketConfig,
    LocalDBConfig,
    LocalOllamaConfig,
    LocalRedisConfig,
    OllamaConfig,
    RedisConfig,
)
from arkitekt_next.server.services.base import (
    BaseServiceConfig,
    ServiceRole,
    ServiceScope,
)


class AlpakaConfig(BaseServiceConfig):
    """Configuration for the Alpaka service."""

    _identifier: ClassVar[str] = "alpaka"
    _name: ClassVar[str] = "Alpaka"
    _description: ClassVar[str] = "AI/ML model management"

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="modeler", description="Can manage ML models"),
        ServiceRole(key="viewer", description="Read-only access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="alpaka_infer", description="Run inference on models"),
        ServiceScope(key="alpaka_train", description="Train ML models"),
        ServiceScope(key="alpaka_manage", description="Manage model registry"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=False,
        description="Whether the Alpaka service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/alpaka:next",
        description="Docker image for the Alpaka service",
    )
    host: str = Field(
        default="alpaka",
        description="Host for the Alpaka service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/alpaka-server",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="alpakamedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="alpaka"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )
    ollama_config: OllamaConfig = Field(
        default_factory=LocalOllamaConfig,
        description="Ollama LLM configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Alpaka."""
        return {"media": self.media_bucket}
