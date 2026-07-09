"""Coordinator deployment profile configuration.

A **coordinator** runs ONLY Lok (the auth authority, which also serves the
Kontrol web frontend) plus Lok's dependencies (Postgres, Redis, MinIO, and the
Caddy gateway). It runs no data/compute services. Because it IS the identity
authority, this schema carries organizations/users/memberships/admin -- but it
deliberately has NO data-service fields. It is a deep, standalone schema written
to its own ``coord_config.yaml`` and consumed by ``diff.write_coord_files``.

``coord_server`` is implicitly ``"local"`` for a coordinator (it is the
coordination server), so it is not a field here.
"""

from pydantic import BaseModel, ConfigDict, Field

from arkitekt_next.server.device_id import get_or_set_device_id

from .infrastructure import (
    DatenConfig,
    GatewayConfig,
    MinioConfig,
    RedisServiceConfig,
)
from .kommunity import KommunityPartner
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

from arkitekt_next.server.services import LokConfig


class CoordConfig(BaseModel):
    """Configuration for a coordinator deployment (Lok + Kontrol only)."""

    device_id: str | None = Field(
        default_factory=get_or_set_device_id,
        description="Device ID for this coordinator instance",
    )
    default_service_grace_period_seconds: int = Field(
        default=2,
        description="Default grace period before shutting down a service",
    )
    domain: str | None = Field(
        default=None,
        description="Domain for the coordinator. If None, runs on localhost",
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
        description="Global description for the coordinator",
    )

    # Infrastructure services (a coordinator runs Lok + its deps only -- no deployer)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    local_redis: RedisServiceConfig = Field(default_factory=RedisServiceConfig)
    db: DatenConfig = Field(default_factory=DatenConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)

    # The one and only service (NO data/compute services on a coordinator)
    lok: LokConfig = Field(default_factory=LokConfig)

    # Identity / provisioning (this IS the auth authority)
    organizations: list[Organization] = Field(
        default_factory=lambda: [create_default_organization()],
    )
    users: list[User] = Field(default_factory=create_default_users)
    memberships: list[Membership] = Field(default_factory=create_default_memberships)
    roles: list[Role] = Field(default_factory=list)
    global_admin: str = Field(default="admin")
    global_admin_password: str = Field(
        default_factory=generate_alpha_numeric_string,
    )
    global_admin_email: str | None = Field(default=None)
    email: EmailConfig | None = Field(default=None)
    kommunity_partners: list[KommunityPartner] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
