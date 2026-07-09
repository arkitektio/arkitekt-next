"""Kabinet service - Container and deployment management.

Kabinet provides container management and deployment capabilities,
enabling users to deploy and manage containerized applications.
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


class KabinetConfig(BaseServiceConfig):
    """Configuration for the Kabinet service."""

    _identifier: ClassVar[str] = "kabinet"
    _name: ClassVar[str] = "Kabinet"
    _description: ClassVar[str] = "Container and deployment management"

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="deployer", description="Can deploy containers"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="viewer", description="Read-only access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(
            key="kabinet_add_repo", description="Add repositories to the database"
        ),
        ServiceScope(key="kabinet_deploy", description="Deploy containers"),
        ServiceScope(key="kabinet_read", description="Read container definitions"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Kabinet service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/kabinet:next",
        description="Docker image for the Kabinet service",
    )
    host: str = Field(
        default="kabinet",
        description="Host for the Kabinet service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/kabinet-server",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="kabinetmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="kabinet"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )
    ensured_repositories: list[str] = Field(
        default_factory=lambda: [
            "jhnnsrs/ome:main",
            "jhnnsrs/renderer:main",
        ],
        description="List of repositories ensured to be present",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Kabinet."""
        return {"media": self.media_bucket}
