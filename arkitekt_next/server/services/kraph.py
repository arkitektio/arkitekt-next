"""Kraph service - Knowledge graph and data relationships.

Kraph provides knowledge graph capabilities for Arkitekt,
enabling users to create and query relationships between data entities.
"""

from typing import ClassVar, Dict

from pydantic import Field

from arkitekt_next.server.config import (
    BucketConfig,
    DBConfig,
    LocalBucketConfig,
    LocalDBConfig,
    LocalRedisConfig,
    RedisConfig,
)
from arkitekt_next.server.services.base import (
    BaseServiceConfig,
    ServiceRole,
    ServiceScope,
)


class KraphConfig(BaseServiceConfig):
    """Configuration for the Kraph service."""

    _identifier: ClassVar[str] = "kraph"
    _name: ClassVar[str] = "Kraph"
    _description: ClassVar[str] = "Knowledge graph and data relationships"
    _uses_datalayer: ClassVar[bool] = True

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="editor", description="Can edit graph data"),
        ServiceRole(key="viewer", description="Read-only access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="kraph_read", description="Read graph data"),
        ServiceScope(key="kraph_write", description="Write graph data"),
        ServiceScope(key="kraph_query", description="Execute graph queries"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Kraph service is enabled",
    )
    image: str = Field(
        # kraph has no :next image published yet; its :dev line already speaks the
        # new config schema.
        default="jhnnsrs/kraph:dev",
        description="Docker image for the Kraph service",
    )
    host: str = Field(
        default="kraph",
        description="Host for the Kraph service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/kraph-server",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="kraphmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="kraph"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Kraph."""
        return {"media": self.media_bucket}
