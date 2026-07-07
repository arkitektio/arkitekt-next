"""Kommunity partner models.

This module contains models for kommunity partners, which are
external service integrations that can be pre-authorized or auto-configured.
"""

import secrets
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ServiceAlias(BaseModel):
    """Configuration for a service alias in the kommunity partner."""

    challenge: str = Field(default="ht", description="Challenge type for the alias")
    host: str = Field(description="Host for the alias (relative to composition)")
    id: str = Field(description="Unique identifier for the alias")
    port: int = Field(default=80, description="Port for the alias")
    kind: Literal["relative", "absolute"] = Field(
        default="relative",
        description="Kind of alias (relative to gateway or absolute)",
    )
    name: str = Field(description="Display name for the alias")
    scope: Literal["public", "private"] = Field(
        default="public", description="Scope of the alias"
    )
    ssl: bool = Field(default=False, description="Whether to use SSL")


class ServiceManifest(BaseModel):
    """Manifest for a service in the kommunity partner."""

    description: str = Field(description="Description of the service")
    identifier: str = Field(description="Unique identifier for the service")
    name: str = Field(description="Display name for the service")
    node_id: str = Field(
        default_factory=lambda: secrets.token_hex(16),
        description="Node ID for the service",
    )
    public_sources: list[dict] = Field(
        default_factory=list, description="Public sources for the service"
    )
    roles: list[dict] = Field(default_factory=list, description="Roles for the service")
    scopes: list[dict] = Field(
        default_factory=list, description="Scopes for the service"
    )
    version: str = Field(default="1.0.0", description="Version of the service")


class ServiceInstance(BaseModel):
    """Instance of a service in the kommunity partner composition."""

    identifier: str = Field(description="Unique identifier for the instance")
    aliases: list[ServiceAlias] = Field(
        default_factory=list, description="Aliases for the instance"
    )
    manifest: ServiceManifest = Field(description="Manifest for the service")


class PreconfiguredComposition(BaseModel):
    """Preconfigured composition for a kommunity partner."""

    identifier: str = Field(description="Unique identifier for the composition")
    instances: list[ServiceInstance] = Field(
        default_factory=list, description="Service instances in the composition"
    )


class KommunityPartner(BaseModel):
    """Configuration for a kommunity partner (external service integration)."""

    identifier: str = Field(description="Unique identifier for the partner")
    name: str = Field(description="Display name for the partner")
    website_url: str = Field(
        default="localhost", description="Website URL for the partner"
    )
    partner_kind: Literal["preauthorized", "autoconfigured"] = Field(
        default="preauthorized",
        description="Kind of partner: 'preauthorized' or 'autoconfigured'",
    )
    auto_configure: bool = Field(
        default=True, description="Whether to auto-configure this partner"
    )
    preconfigured_composition: PreconfiguredComposition | None = Field(
        default=None, description="Preconfigured composition for this partner"
    )

    model_config = ConfigDict(
        extra="forbid",
    )


def create_local_service_aliases(
    service_configs: list[tuple[str, str, int, str]],
) -> list[ServiceInstance]:
    """
    Create service instances with relative aliases for local services.

    Args:
        service_configs: List of tuples (service_identifier, service_name, port, manifest_identifier)

    Returns:
        List of ServiceInstance objects configured for local access
    """
    instances = []
    for service_id, service_name, port, manifest_id in service_configs:
        instances.append(
            ServiceInstance(
                identifier=service_name,
                aliases=[
                    ServiceAlias(
                        challenge="ht",
                        host=service_id,
                        id=f"local_{service_id}",
                        port=port,
                        kind="relative",
                        name=service_name,
                        scope="public",
                        ssl=False,
                    )
                ],
                manifest=ServiceManifest(
                    description=f"{service_name} Service for local Arkitekt",
                    identifier=manifest_id,
                    name=service_name,
                    public_sources=[],
                    roles=[{"key": "user", "description": "Default user role"}],
                    scopes=[
                        {"key": "read", "description": "Read access"},
                        {"key": "write", "description": "Write access"},
                    ],
                ),
            )
        )
    return instances


def create_default_kommunity_partners() -> list[KommunityPartner]:
    """
    Create default kommunity partners that point to local services.

    These provide 'autoconfigured' and 'preauthorized' access to the local Arkitekt services.
    """
    # Define local services with their configuration
    local_services = [
        ("rekuest", "Rekuest Service", 80, "live.arkitekt.rekuest"),
        ("mikro", "Mikro Service", 80, "live.arkitekt.mikro"),
        ("fluss", "Fluss Service", 80, "live.arkitekt.fluss"),
        ("kabinet", "Kabinet Service", 80, "live.arkitekt.kabinet"),
        ("lok", "Lok Service", 80, "live.arkitekt.lok"),
        ("kraph", "Kraph Service", 80, "live.arkitekt.kraph"),
    ]

    return [
        KommunityPartner(
            identifier="local_arkitekt",
            name="Local Arkitekt Services",
            website_url="localhost",
            partner_kind="autoconfigured",
            auto_configure=True,
            preconfigured_composition=PreconfiguredComposition(
                identifier="localhost",
                instances=create_local_service_aliases(local_services),
            ),
        ),
        KommunityPartner(
            identifier="preauthorized_local",
            name="Preauthorized Local Access",
            website_url="localhost",
            partner_kind="preauthorized",
            auto_configure=True,
            preconfigured_composition=PreconfiguredComposition(
                identifier="localhost",
                instances=create_local_service_aliases(local_services),
            ),
        ),
    ]
