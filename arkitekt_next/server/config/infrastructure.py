"""Infrastructure service configurations.

This module contains configurations for infrastructure services
that support the Arkitekt platform (database, storage, caching, gateway).
"""

import secrets

from pydantic import BaseModel, Field

from .utils import generate_alpha_numeric_string, generate_name


class MinioConfig(BaseModel):
    """Configuration for MinIO object storage service."""

    host: str = Field(default="minio", description="Host for the MinIO service")
    enabled: bool = Field(
        default=True, description="Whether the MinIO service is enabled"
    )
    internal_port: int = Field(
        default=9000, description="Internal port for the MinIO service"
    )
    access_key: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Access key for the MinIO service",
    )
    secret_key: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Secret key for the MinIO service",
    )
    root_user: str = Field(
        default_factory=generate_name,
        description="Root user for the MinIO service",
    )
    root_password: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Root password for the MinIO service",
    )
    init_container_host: str = Field(
        default="minio_init",
    )
    init_container_image: str = Field(
        default="jhnnsrs/init:dev",
        description="Docker image for the MinIO init container",
    )
    image: str = Field(
        default="minio/minio:RELEASE.2025-02-18T16-25-55Z",
        description="Docker image for the MinIO service",
    )
    mount: str | None = Field(
        default="/data",
        description="Mount point for MinIO data storage. If None, a volume will be created.",
    )
    volume_name: str = Field(
        default="minio_data",
        description="Name of the volume for MinIO data storage",
    )
    console_port: int = Field(
        default=9001,
        description="Port for the MinIO console",
    )
    exposed_console_port: int | None = Field(
        default=None,
        description="Exposed port for the MinIO console. If None, the console will not be exposed",
    )


class DatenConfig(BaseModel):
    """Configuration for Daten (PostgreSQL) database service."""

    enabled: bool = Field(
        default=True, description="Whether the Daten service is enabled"
    )
    image: str = Field(
        default="jhnnsrs/daten:dev",
        description="Docker image for the Daten service",
    )
    host: str = Field(default="daten", description="Host for the Daten service")
    postgres_user: str = Field(
        default="sleepyviolettarsier",
        description="PostgreSQL user for the Daten service",
    )
    postgres_password: str = Field(
        default="30ae0f6d873a75e6ca8d25f98033f849",
        description="PostgreSQL password for the Daten service",
    )
    github_repo: str = Field(
        default="https://github.com/arkitektio/daten-server",
        description="GitHub repository URL for the Daten service",
    )
    mount: str | None = Field(
        default="./db_data",
        description="Mount point for PostgreSQL database storage. If None, a volume will be created.",
    )
    volume_name: str = "db_data"


class RedisServiceConfig(BaseModel):
    """Configuration for Redis caching service."""

    host: str = Field(default="redis", description="Host for the Redis service")
    image: str = Field(
        default="redis:latest",
        description="Docker image for the Redis service",
    )
    internal_port: int = Field(
        default=6379,
        description="Internal port for the Redis service",
    )
    enabled: bool = Field(
        default=True, description="Whether the Redis service is enabled"
    )


class GatewayConfig(BaseModel):
    """Configuration for the Caddy gateway/reverse proxy service."""

    enabled: bool = Field(
        default=True, description="Whether the Gateway service is enabled"
    )
    host: str = Field(default="gateway", description="Host for the Gateway service")
    image: str = Field(
        default="caddy:latest",
        description="Docker image for the Gateway service (Caddy)",
    )
    internal_port: int = Field(
        default=80,
        description="Internal port for the Gateway service",
    )
    ssl: bool = Field(
        default=False,
        description="Whether to enable SSL for the Arkitekt server",
    )
    ssl_cert: str | None = Field(
        default=None,
        description="Path to the SSL certificate file. If None, uses Let's Encrypt",
    )
    auto_https: bool = Field(
        default=True,
        description="Whether to automatically force HTTPS",
    )
    exposed_http_port: int | None = Field(
        default=80,
        description="Port for the HTTP server exposed to the outside world",
    )
    exposed_https_port: int | None = Field(
        default=443,
        description="Port for the HTTPS server exposed to the outside world",
    )


class DeployerConfig(BaseModel):
    """Configuration for the Deployer service."""

    host: str = Field(default="deployer", description="Host for the Deployer service")
    image: str = Field(
        default="jhnnsrs/deployer:dev",
        description="Docker image for the Deployer service",
    )
    enabled: bool = Field(
        default=True, description="Whether the Deployer service is enabled"
    )
    redeem_token: str = Field(
        default_factory=lambda: secrets.token_hex(16),
        description="Redeem token for authenticating requests to the Deployer service",
    )
    instance_id: str = Field(
        default="INTERNAL_DOCKER",
        description="Instance ID for the Deployer service",
    )
    user: str = Field(
        default="deployer",
        description="User for the Deployer service",
    )
