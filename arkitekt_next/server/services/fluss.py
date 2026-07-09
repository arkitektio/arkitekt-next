"""Fluss service - Workflow definition and management.

Fluss provides the workflow definition and management layer for Arkitekt,
enabling users to create and manage data processing workflows.
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


class FlussConfig(BaseServiceConfig):
    """Configuration for the Fluss service."""

    _identifier: ClassVar[str] = "fluss"
    _name: ClassVar[str] = "Fluss"
    _description: ClassVar[str] = "Workflow definition and management"

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="designer", description="Can design workflows"),
        ServiceRole(key="viewer", description="Read-only access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="fluss_read", description="Read workflow definitions"),
        ServiceScope(key="fluss_write", description="Create and modify workflows"),
        ServiceScope(key="fluss_execute", description="Execute workflows"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Fluss service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/fluss:next",
        description="Docker image for the Fluss service",
    )
    host: str = Field(
        default="fluss",
        description="Host for the Fluss service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/fluss-server-next",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="flussmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="fluss"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Fluss."""
        return {"media": self.media_bucket}
