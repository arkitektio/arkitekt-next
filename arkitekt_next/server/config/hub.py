"""Hub deployment profile configuration.

A **hub** runs local data/compute services (rekuest, mikro, fluss, ...) but NO
local coordinator: it trusts a remote coordination (auth) server for identity.
Consequently this schema deliberately carries **no** ``lok``, ``organizations``,
``users``, ``memberships`` or ``kommunity_partners`` fields -- a hub manages no
identities. It is a deep, standalone schema (not a subset view of
``ArkitektServerConfig``) written to its own ``hub_config.yaml`` and consumed by
the dedicated ``diff.write_hub_files`` generator.
"""

from pydantic import BaseModel, ConfigDict, Field

from arkitekt_next.server.device_id import get_or_set_device_id

from .infrastructure import (
    DatenConfig,
    GatewayConfig,
    MinioConfig,
    RedisServiceConfig,
)
from .utils import generate_alpha_numeric_string, generate_name

# Service configs are imported from the services package (mirrors config/server.py).
from arkitekt_next.server.services import (
    AlpakaConfig,
    ElektroConfig,
    FlussConfig,
    KabinetConfig,
    KraphConfig,
    LovekitConfig,
    MikroConfig,
    RekuestConfig,
)


class HubConfig(BaseModel):
    """Configuration for a hub deployment (services, no local coordinator)."""

    device_id: str | None = Field(
        default_factory=get_or_set_device_id,
        description="Device ID for this hub instance",
    )
    default_service_grace_period_seconds: int = Field(
        default=2,
        description="Default grace period before shutting down a service",
    )
    domain: str | None = Field(
        default=None,
        description="Domain for the hub. If None, runs on localhost",
    )
    coord_server: str = Field(
        default="go.arkitekt.live",
        description="Remote coordination (auth) server host whose JWKS the local "
        "services trust for inbound tokens.",
    )
    rekuest_server: str = Field(
        default="local",
        description="Rekuest (provenance authority) host. 'local' runs rekuest as a "
        "core dependency; otherwise services trust a remote rekuest.",
    )
    internal_network: str = Field(
        default_factory=generate_name,
        description="Internal docker network name connecting the services",
    )
    csrf_trusted_origins: list[str] | None = Field(
        default=None,
        description="List of trusted origins for CSRF protection",
    )
    global_description: str | None = Field(
        default=None,
        description="Global description for the hub",
    )
    # A Django superuser is still needed for each service's local admin panel. This
    # is a server-level setting, NOT a Lok identity -- the hub asks no org/user info.
    global_admin: str = Field(
        default="admin",
        description="Django superuser username for the local service admin panels",
    )
    global_admin_password: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Django superuser password",
    )
    global_admin_email: str | None = Field(
        default=None,
        description="Django superuser email",
    )

    # Infrastructure services (a hub has NO deployer -- see the `engine` command)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    local_redis: RedisServiceConfig = Field(default_factory=RedisServiceConfig)
    db: DatenConfig = Field(default_factory=DatenConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)

    # Data / compute services (NO lok -- a hub has no local coordinator)
    rekuest: RekuestConfig = Field(default_factory=RekuestConfig)
    mikro: MikroConfig = Field(default_factory=MikroConfig)
    fluss: FlussConfig = Field(default_factory=FlussConfig)
    kabinet: KabinetConfig = Field(default_factory=KabinetConfig)
    kraph: KraphConfig = Field(default_factory=KraphConfig)
    elektro: ElektroConfig = Field(default_factory=ElektroConfig)
    alpaka: AlpakaConfig = Field(default_factory=AlpakaConfig)
    lovekit: LovekitConfig = Field(default_factory=LovekitConfig)

    model_config = ConfigDict(extra="forbid")
