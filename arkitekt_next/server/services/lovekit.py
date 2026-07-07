"""Lovekit service - Real-time communication.

Lovekit provides LiveKit integration for real-time audio/video
communication within Arkitekt.
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


class LovekitConfig(BaseServiceConfig):
    """Configuration for the Lovekit service."""

    _identifier: ClassVar[str] = "lovekit"
    _name: ClassVar[str] = "Lovekit"
    _description: ClassVar[str] = "LiveKit integration for real-time communication"
    # Lovekit does not consume provenance attestation tokens.
    _verifies_provenance: ClassVar[bool] = False

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="broadcaster", description="Can broadcast streams"),
        ServiceRole(key="viewer", description="Can view streams"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="lovekit_stream", description="Stream audio/video"),
        ServiceScope(key="lovekit_view", description="View streams"),
        ServiceScope(key="lovekit_manage", description="Manage rooms and sessions"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Lovekit service is enabled",
    )
    host: str = Field(
        default="lovekit",
        description="Host for the Lovekit service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/lovekit-server",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="lovekitmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="lovekit"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Lovekit."""
        return {"media": self.media_bucket}
