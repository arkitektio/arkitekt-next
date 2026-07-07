"""Base classes and protocols for services and apps.

This module defines the base configuration classes and protocols
that all Arkitekt services must implement.

Note: BaseServiceConfig is defined in arkitekt_next.server.services.base
to avoid circular imports. It's re-exported via the config package.
"""

from typing import Dict, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from .types import (
    AdminConfig,
    AuthConfig,
    BucketConfig,
    GlobalAdminConfig,
    LocalAuthConfig,
    LocalPath,
    PathConfig,
)


@runtime_checkable
class ServiceProtocol(Protocol):
    """Protocol defining the interface for all Arkitekt services.

    This protocol defines the minimum attributes and methods that
    all service configurations must provide.
    """

    enabled: bool
    host: str
    image: str
    path_config: PathConfig
    auth_config: AuthConfig
    admin_config: AdminConfig
    debug: bool
    allowed_hosts: list[str]
    secret_key: str
    internal_port: int
    mount_github: bool
    github_repo: str

    def get_buckets(self) -> Dict[str, BucketConfig]:
        """Get the storage buckets for this service."""
        ...

    def build_run_command(self) -> str:
        """Build the command to run this service."""
        ...


@runtime_checkable
class AppProtocol(Protocol):
    """Protocol for Arkitekt applications."""

    host: str
    image: str
    run_as_user: str | None
    run_in_organization: str | None


class BaseAppConfig(BaseModel):
    """Base configuration for Arkitekt applications."""

    grace_period_seconds: int | None = Field(
        default=None,
        description="Grace period before shutdown (uses global if None)",
    )
    instances: list[str] = Field(
        default_factory=lambda: ["main"],
        description="List of instances for the app",
    )
    host: str = Field(description="Host for the app")
    image: str = Field(description="Docker image for the app")
    user: str | None = Field(
        default=None,
        description="User to run the app as",
    )
    organization: str | None = Field(
        default=None,
        description="Organization to run the app in",
    )


class AdditionalAppConfig(BaseAppConfig):
    """Configuration for additional custom apps."""

    pass


class BaseStackConfig(BaseModel):
    """Base configuration for a service stack."""

    description: str | None = Field(
        default=None,
        description="Description of the stack",
    )
    # Note: Uses Any to avoid circular import with BaseServiceConfig
    services: list = Field(
        default_factory=list,
        description="List of services in the stack",
    )
