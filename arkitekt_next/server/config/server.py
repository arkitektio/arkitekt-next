"""Main Arkitekt server configuration.

This module contains the main ArkitektServerConfig class that
brings together all service configurations and platform settings.
"""

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from arkitekt_next.server.device_id import get_or_set_device_id

from .infrastructure import (
    DatenConfig,
    DeployerConfig,
    GatewayConfig,
    MinioConfig,
    RedisServiceConfig,
)
from .kommunity import KommunityPartner, create_default_kommunity_partners
from .users import (
    EmailConfig,
    Membership,
    Organization,
    Role,
    User,
    create_default_memberships,
    create_default_organization,
    create_default_users,
)
from .utils import generate_alpha_numeric_string, generate_name

# Import service configs - these are needed for the fields
from arkitekt_next.server.services import (
    AlpakaConfig,
    ElektroConfig,
    FlussConfig,
    KabinetConfig,
    KraphConfig,
    LokConfig,
    LovekitConfig,
    MikroConfig,
    RekuestConfig,
)


class AdditionalAppConfig(BaseModel):
    """Configuration for additional custom apps."""

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


class ArkitektServerConfig(BaseModel):
    """Main configuration for the Arkitekt server.

    This is the top-level configuration that brings together all
    service configurations, user management, and platform settings.
    """

    device_id: str | None = Field(
        default_factory=get_or_set_device_id,
        description="Device ID for the Arkitekt server instance",
    )
    default_service_grace_period_seconds: int = Field(
        default=2,
        description="Default grace period before shutting down a service",
    )
    domain: str | None = Field(
        default=None,
        description="Domain for the Arkitekt server. If None, runs on localhost",
    )
    coord_server: str = Field(
        default="go.arkitekt.live",
        description="Coordination (auth) server host whose JWKS authentikate trusts. "
        "Set to 'local' to run Lok as the coordination server.",
    )
    rekuest_server: str = Field(
        default="local",
        description="Rekuest server (provenance authority) host whose JWKS verifies "
        "attestations. 'local' runs rekuest locally as a core dependency; a host trusts "
        "a remote rekuest.",
    )
    internal_network: str = Field(
        default_factory=generate_name,
        description="Internal network name for connecting services",
    )
    email: EmailConfig | None = Field(
        default=None,
        description="Email configuration for sending emails",
    )
    global_description: str | None = Field(
        default=None,
        description="Global description for the Arkitekt server",
    )
    csrf_trusted_origins: list[str] | None = Field(
        default=None,
        description="List of trusted origins for CSRF protection",
    )

    # Infrastructure services
    gateway: GatewayConfig = Field(
        default_factory=GatewayConfig,
        description="Configuration for the Gateway service",
    )
    deployer: DeployerConfig = Field(
        default_factory=DeployerConfig,
        description="Configuration for the Deployer service",
    )
    local_redis: RedisServiceConfig = Field(
        default_factory=RedisServiceConfig,
        description="Local Redis configuration",
    )
    db: DatenConfig = Field(
        default_factory=DatenConfig,
        description="Configuration for the database service",
    )
    minio: MinioConfig = Field(
        default_factory=MinioConfig,
        description="Configuration for the MinIO service",
    )

    # User management
    organizations: list[Organization] = Field(
        default_factory=lambda: [create_default_organization()],
        description="List of organizations",
    )
    users: list[User] = Field(
        default_factory=lambda: create_default_users(),
        description="List of users",
    )
    memberships: list[Membership] = Field(
        default_factory=lambda: create_default_memberships(),
        description="List of memberships linking users to organizations",
    )
    roles: list[Role] = Field(
        default_factory=lambda: [],
        description="List of custom roles",
    )
    global_admin: str = Field(
        default="admin",
        description="Global admin username",
    )
    global_admin_password: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Global admin password",
    )
    global_admin_email: str | None = Field(
        default=None,
        description="Global admin email",
    )

    # Kommunity partners
    kommunity_partners: list[KommunityPartner] = Field(
        default_factory=list,
        description="List of kommunity partners (external service integrations)",
    )

    # Additional apps
    apps: dict[str, AdditionalAppConfig] = Field(
        default_factory=dict,
        description="Additional applications to run",
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    # Service configurations
    rekuest: RekuestConfig = Field(
        default_factory=RekuestConfig,
        description="Configuration for the Rekuest service",
    )
    lok: LokConfig = Field(
        default_factory=LokConfig,
        description="Configuration for the Lok service",
    )
    mikro: MikroConfig = Field(
        default_factory=MikroConfig,
        description="Configuration for the Mikro service",
    )
    fluss: FlussConfig = Field(
        default_factory=FlussConfig,
        description="Configuration for the Fluss service",
    )
    kabinet: KabinetConfig = Field(
        default_factory=KabinetConfig,
        description="Configuration for the Kabinet service",
    )
    kraph: KraphConfig = Field(
        default_factory=KraphConfig,
        description="Configuration for the Kraph service",
    )
    elektro: ElektroConfig = Field(
        default_factory=ElektroConfig,
        description="Configuration for the Elektro service",
    )
    alpaka: AlpakaConfig = Field(
        default_factory=AlpakaConfig,
        description="Configuration for the Alpaka service",
    )
    lovekit: LovekitConfig = Field(
        default_factory=LovekitConfig,
        description="Configuration for the Lovekit service",
    )


class Setup(BaseModel):
    """Setup configuration for deploying the Arkitekt server."""

    backend: Literal["docker", "podman", "kubernetes"] = Field(
        default="docker",
        description="Backend for deployment",
    )
    config: ArkitektServerConfig = Field(
        default_factory=ArkitektServerConfig,
        description="Configuration for the Arkitekt server",
    )
