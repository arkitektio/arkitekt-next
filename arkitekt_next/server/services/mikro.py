"""Mikro service - Microscopy data management.

Mikro provides microscopy image and data management for Arkitekt,
handling large image datasets with multi-dimensional support.
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


class MikroConfig(BaseServiceConfig):
    """Configuration for the Mikro service."""

    _identifier: ClassVar[str] = "mikro"
    _name: ClassVar[str] = "Mikro"
    _description: ClassVar[str] = "Microscopy data management and analysis"
    _uses_datalayer: ClassVar[bool] = True

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="viewer", description="Read-only access to images"),
        ServiceRole(key="uploader", description="Can upload new images"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="mikro_read", description="Read images from the database"),
        ServiceScope(key="mikro_write", description="Write images to the database"),
        ServiceScope(key="read_image", description="Read image data"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Mikro service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/mikro:next",
        description="Docker image for the Mikro service",
    )
    host: str = Field(
        default="mikro",
        description="Host for the Mikro service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/mikro-server-next",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="mikromedia"),
        description="Media storage bucket",
    )
    zarr_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="mikrozarr"),
        description="Zarr array storage bucket",
    )
    parquet_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="mikroparquet"),
        description="Parquet table storage bucket",
    )
    bigfile_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="mikrobigfile"),
        description="Large binary file storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="mikro"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Mikro (datalayer purpose -> bucket)."""
        return {
            "media": self.media_bucket,
            "zarr": self.zarr_bucket,
            "parquet": self.parquet_bucket,
            "bigfile": self.bigfile_bucket,
        }
