"""Lok service - Authentication and authorization.

Lok provides centralized authentication and authorization for Arkitekt,
managing users, organizations, and access tokens.
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
    build_key_pair,
)
from arkitekt_next.server.services.base import (
    BaseServiceConfig,
    ServiceRole,
    ServiceScope,
)


class LokConfig(BaseServiceConfig):
    """Configuration for the Lok authentication service."""

    _identifier: ClassVar[str] = "lok"
    _name: ClassVar[str] = "Lok"
    _description: ClassVar[str] = "Authentication and authorization (required)"
    _uses_datalayer: ClassVar[bool] = True
    # Lok is the auth authority; it does not consume provenance attestation tokens.
    _verifies_provenance: ClassVar[bool] = False

    _roles: ClassVar[list[ServiceRole]] = [
        ServiceRole(key="admin", description="Full administrative access"),
        ServiceRole(key="user", description="Standard user access"),
        ServiceRole(key="bot", description="Automated bot access"),
        ServiceRole(key="viewer", description="Read-only access"),
        ServiceRole(key="editor", description="Read and write access"),
    ]

    _scopes: ClassVar[list[ServiceScope]] = [
        ServiceScope(key="openid", description="OpenID Connect scope"),
        ServiceScope(key="read", description="Generic read access"),
        ServiceScope(key="write", description="Generic write access"),
        ServiceScope(key="profile", description="Access user profile"),
        ServiceScope(key="email", description="Access user email"),
    ]

    enabled: bool = Field(
        default=True,
        description="Whether the Lok service is enabled",
    )
    image: str = Field(
        default="jhnnsrs/lok:next",
        description="Docker image for the Lok service",
    )
    host: str = Field(
        default="lok",
        description="Host for the Lok service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/lok-server-next",
        description="GitHub repository URL",
    )
    issuer: str = Field(
        default="lok",
        description="OAuth2 issuer identifier",
    )
    media_bucket: BucketConfig = Field(
        default_factory=lambda: LocalBucketConfig(bucket_name="lokmedia"),
        description="Media storage bucket",
    )
    db_config: DBConfig = Field(
        default_factory=lambda: LocalDBConfig(db="lok"),
        description="Database configuration",
    )
    redis_config: RedisConfig = Field(
        default_factory=LocalRedisConfig,
        description="Redis configuration",
    )
    auth_key_pair: KeyPair = Field(
        default_factory=build_key_pair,
        description="Key pair for signing tokens",
    )

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get storage buckets for Lok."""
        return {"media": self.media_bucket}
