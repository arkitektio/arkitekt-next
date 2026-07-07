"""Elektro service - Electrophysiology data management.

Elektro provides electrophysiology data management for Arkitekt,
handling electrophysiological recordings and analysis.
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


class ElektroConfig(BaseServiceConfig):
    """Configuration for the Elektro service."""

    _identifier: ClassVar[str] = "elektro"
    _name: ClassVar[str] = "Elektro"
    _description: ClassVar[str] = "Electrophysiology data management"
    _uses_datalayer: ClassVar[bool] = True

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="analyst", description="Can analyze recordings"),
        ServiceRole(key="viewer", description="Read-only access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="elektro_read", description="Read electrophysiology data"),
        ServiceScope(key="elektro_write", description="Write electrophysiology data"),
        ServiceScope(key="elektro_analyze", description="Run analysis on recordings"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=False,
        description="Whether the Elektro service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/elektro:next",
        description="Docker image for the Elektro service",
    )
    host: str = Field(
        default="elektro",
        description="Host for the Elektro service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/elektro-server",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="elektromedia"),
        description="Media storage bucket",
    )
    zarr_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="elektrozarr"),
        description="Zarr array storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="elektro"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Elektro (datalayer purpose -> bucket)."""
        return {"media": self.media_bucket, "zarr": self.zarr_bucket}
