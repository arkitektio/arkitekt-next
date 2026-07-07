"""Type definitions for configuration options.

This module defines the discriminated union types used throughout
the configuration system for database, storage, authentication, etc.
"""

import secrets
from typing import Literal, Union

from pydantic import BaseModel, Field

from .utils import generate_name


# =============================================================================
# Storage Configuration Types
# =============================================================================


class S3BucketConfig(BaseModel):
    """Configuration for an S3-compatible bucket."""

    kind: Literal["s3"] = Field(default="s3")
    access_key: str = Field(description="Access key for the S3 bucket")
    secret_key: str = Field(description="Secret key for the S3 bucket")
    region: str = Field(default="us-east-1", description="Region for the S3 bucket")
    endpoint_url: str = Field(description="Endpoint URL for the S3 bucket")
    bucket_name: str = Field(description="Name of the S3 bucket")


class LocalBucketConfig(BaseModel):
    """Configuration for a local MinIO bucket."""

    kind: Literal["local"] = Field(default="local")
    bucket_name: str = Field(
        default_factory=generate_name,
        description="Name of the local bucket",
    )


BucketConfig = Union[S3BucketConfig, LocalBucketConfig]


# =============================================================================
# Database Configuration Types
# =============================================================================


class RemoteDBConfig(BaseModel):
    """Configuration for a remote PostgreSQL database."""

    kind: Literal["remote"] = Field(default="remote")
    host: str = Field(description="Host for the remote database")
    port: int = Field(default=5432, description="Port for the remote database")
    user: str = Field(description="User for the remote database")
    password: str = Field(description="Password for the remote database")
    db: str = Field(description="Database name")


class LocalDBConfig(BaseModel):
    """Configuration for a local PostgreSQL database."""

    kind: Literal["local"] = Field(default="local")
    db: str = Field(default="mikro", description="Database name")


DBConfig = Union[RemoteDBConfig, LocalDBConfig]


# =============================================================================
# Admin Configuration Types
# =============================================================================


class SpecificAdminConfig(BaseModel):
    """Configuration for a service-specific admin user."""

    kind: Literal["specific"] = Field(default="specific")
    username: str = Field(description="Username for the admin user")
    password: str = Field(description="Password for the admin user")
    email: str | None = Field(default=None, description="Email for the admin user")


class GlobalAdminConfig(BaseModel):
    """Use the global admin user for the service."""

    kind: Literal["global"] = Field(default="global")


AdminConfig = Union[SpecificAdminConfig, GlobalAdminConfig]


# =============================================================================
# Redis Configuration Types
# =============================================================================


class LocalRedisConfig(BaseModel):
    """Configuration for local Redis."""

    kind: Literal["local"] = Field(default="local")


class RemoteRedisConfig(BaseModel):
    """Configuration for remote Redis."""

    kind: Literal["remote"] = Field(default="remote")
    host: str = Field(description="Host for the remote Redis server")
    port: int = Field(default=6379, description="Port for the remote Redis server")


RedisConfig = Union[LocalRedisConfig, RemoteRedisConfig]


# =============================================================================
# ChromaDB Configuration Types
# =============================================================================


class LocalChromaDBConfig(BaseModel):
    """Configuration for local ChromaDB."""

    kind: Literal["local"] = Field(default="local")
    db_name: str = Field(description="Database name")


class RemoteChromaDBConfig(BaseModel):
    """Configuration for remote ChromaDB."""

    kind: Literal["remote"] = Field(default="remote")
    host: str = Field(description="Host for the remote ChromaDB")
    port: int = Field(default=8000, description="Port for the remote ChromaDB")
    db_name: str = Field(description="Database name")


ChromaDBConfig = Union[LocalChromaDBConfig, RemoteChromaDBConfig]


# =============================================================================
# Ollama Configuration Types
# =============================================================================


class LocalOllamaConfig(BaseModel):
    """Configuration for local Ollama."""

    kind: Literal["local"] = Field(default="local")


class RemoteOllamaConfig(BaseModel):
    """Configuration for remote Ollama."""

    kind: Literal["remote"] = Field(default="remote")
    host: str = Field(description="Host for the remote Ollama server")
    port: int = Field(default=11434, description="Port for the remote Ollama")


OllamaConfig = Union[LocalOllamaConfig, RemoteOllamaConfig]


# =============================================================================
# Authentication Configuration Types
# =============================================================================


class LocalAuthConfig(BaseModel):
    """Configuration for local authentication with Arkitekt server."""

    kind: Literal["local"] = Field(default="local")


class StaticTokenAuthConfig(BaseModel):
    """Configuration for static token authentication."""

    kind: Literal["static_token"] = Field(default="static_token")
    token: str = Field(
        default_factory=lambda: secrets.token_hex(16),
        description="Static authentication token",
    )
    user: int = Field(default=1, description="User ID for the token")
    issuer: str = Field(default="local_token", description="Token issuer")


AuthConfig = Union[LocalAuthConfig, StaticTokenAuthConfig]


# =============================================================================
# Path Configuration Types
# =============================================================================


class LocalPath(BaseModel):
    """Retrieve path configuration from the gateway."""

    kind: Literal["local"] = Field(default="local")


class ForcePath(BaseModel):
    """Force a specific path configuration."""

    kind: Literal["force"] = Field(default="force")
    path: str = Field(default="/", description="Path to use for this service")


PathConfig = Union[LocalPath, ForcePath]
