"""Rekuest service - Task orchestration and workflow execution.

Rekuest provides the task scheduling and execution framework for Arkitekt,
enabling distributed workflow execution and agent management.
"""

from typing import ClassVar, Dict

from pydantic import Field

from arkitekt_next.server.config import (
    BucketConfig,
    DBConfig,
    KeyPair,
    LocalBucketConfig,
    LocalDBConfig,
    LocalRedisConfig,
    RedisConfig,
    build_ed25519_key_pair,
)
from arkitekt_next.server.services.base import (
    BaseServiceConfig,
    ServiceRole,
    ServiceScope,
)


class RekuestConfig(BaseServiceConfig):
    """Configuration for the Rekuest service."""

    _identifier: ClassVar[str] = "rekuest"
    _name: ClassVar[str] = "Rekuest"
    _description: ClassVar[str] = "Task orchestration and workflow execution"

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="agent", description="Can act as a workflow agent"),
        ServiceRole(key="caller", description="Can call remote procedures"),
        ServiceRole(key="admin", description="Full administrative access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="rekuest_agent", description="Act as an agent"),
        ServiceScope(key="rekuest_call", description="Call other apps with rekuest"),
        ServiceScope(key="read", description="Read access to rekuest resources"),
        ServiceScope(key="write", description="Write access to rekuest resources"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Rekuest service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/rekuest:next",
        description="Docker image for the Rekuest service",
    )
    host: str = Field(
        default="rekuest",
        description="Host for the Rekuest service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/rekuest-server-next",
        description="GitHub repository URL",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="rekuestmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="rekuest"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )
    provenance_issuer: str = Field(
        default="rekuest",
        description="Provenance (attestation) token issuer",
    )
    provenance_kid: str = Field(
        default="rekuest-prov-1",
        description="Provenance key id published at the JWKS endpoint",
    )
    provenance_key_pair: KeyPair = Field(
        default_factory=build_ed25519_key_pair,
        description="Ed25519 key pair for signing provenance attestations",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Rekuest."""
        return {"media": self.media_bucket}
