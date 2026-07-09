"""Base service protocol and abstract implementation.

This module defines the core service abstraction for Arkitekt services.
Each service provides:
- Roles: Permission levels for users within the service
- Scopes: Granular access permissions for API operations
- Configuration: Service-specific settings
"""

from typing import ClassVar, Dict, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from arkitekt_next.server.config.types import (
    AdminConfig,
    AuthConfig,
    BucketConfig,
    DBConfig,
    GlobalAdminConfig,
    LocalAuthConfig,
    LocalPath,
    PathConfig,
    RedisConfig,
)
from arkitekt_next.server.config.utils import generate_django_secret_key


class ServiceScope(BaseModel):
    """Definition of a service scope (permission)."""

    key: str = Field(description="Unique identifier for the scope")
    description: str = Field(description="Human-readable description")


class ServiceRole(BaseModel):
    """Definition of a service role."""

    key: str = Field(description="Unique identifier for the role")
    description: str = Field(description="Human-readable description")


@runtime_checkable
class ServiceProtocol(Protocol):
    """Protocol defining the interface for all Arkitekt services.

    Services must provide:
    - Identity: name, identifier, description
    - Roles and scopes for authorization
    - Configuration for deployment
    """

    # Service identity
    identifier: str
    name: str
    description: str

    # Service configuration
    enabled: bool
    host: str
    image: str
    internal_port: int

    # Deployment configuration
    path_config: PathConfig
    auth_config: AuthConfig
    admin_config: AdminConfig
    db_config: DBConfig
    redis_config: RedisConfig

    # Development options
    debug: bool
    allowed_hosts: list[str]
    secret_key: str
    mount_github: bool
    github_repo: str

    def get_roles(self) -> list[ServiceRole]:
        """Get the roles defined by this service."""
        ...

    def get_scopes(self) -> list[ServiceScope]:
        """Get the scopes (permissions) defined by this service."""
        ...

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get the storage buckets required by this service."""
        ...

    def build_run_command(self) -> str:
        """Build the command to run the service container."""
        ...


class BaseServiceConfig(BaseModel):
    """Base configuration shared by all services.

    This provides common configuration options that all services need,
    including networking, authentication, and development settings.
    """

    # Class-level service metadata (to be overridden by subclasses)
    _identifier: ClassVar[str] = "base"
    _name: ClassVar[str] = "Base Service"
    _description: ClassVar[str] = "Base service configuration"
    _roles: ClassVar[list[ServiceRole]] = []
    _scopes: ClassVar[list[ServiceScope]] = []
    # Whether this service consumes the S3 `datalayer` config block. Services that
    # do not store objects (e.g. fluss, kabinet) must leave this False so no
    # `datalayer` block is emitted into their config.
    _uses_datalayer: ClassVar[bool] = False
    # Whether this service's authentikate config accepts a `provenance` block for
    # verifying inbound provenance (attestation) tokens. Pure auth services like Lok
    # and Lovekit do not consume provenance and reject the block, so they leave this
    # False.
    _verifies_provenance: ClassVar[bool] = True

    internal_port: int = Field(
        default=80,
        description="Internal port for the service",
    )
    mount_github: bool = Field(
        default=False,
        description="Mount GitHub repository for development",
    )
    github_repo: str = Field(
        default="",
        description="GitHub repository URL for the service",
    )
    admin_config: AdminConfig = Field(
        default_factory=GlobalAdminConfig,
        description="Admin configuration for the service",
    )
    auth_config: AuthConfig = Field(
        default_factory=LocalAuthConfig,
        description="Authentication configuration",
    )
    path_config: PathConfig = Field(
        default_factory=LocalPath,
        description="Path configuration for gateway routing",
    )
    allowed_hosts: list[str] = Field(
        default=["*"],
        description="List of allowed hosts (CORS)",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode (not for production)",
    )
    secret_key: str = Field(
        default_factory=generate_django_secret_key,
        description="Secret key for signing",
    )

    @classmethod
    def get_identifier(cls) -> str:
        """Get the service identifier."""
        return cls._identifier

    @classmethod
    def get_name(cls) -> str:
        """Get the display name."""
        return cls._name

    @classmethod
    def get_description(cls) -> str:
        """Get the service description."""
        return cls._description

    @classmethod
    def get_roles(cls) -> list[ServiceRole]:
        """Get the roles defined by this service."""
        return cls._roles.copy()

    @classmethod
    def get_scopes(cls) -> list[ServiceScope]:
        """Get the scopes defined by this service."""
        return cls._scopes.copy()

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get the storage buckets required by this service."""
        return {}

    def build_run_command(self) -> str:
        """Build the command to run the service."""
        if self.debug or self.mount_github:
            return "bash run-debug.sh"
        return "bash run.sh"
