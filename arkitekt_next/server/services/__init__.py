"""Arkitekt Services Module.

This module provides service definitions for all Arkitekt services.
Each service defines its own roles, scopes, and configuration.

Usage:
    from arkitekt_next.server.services import (
        SERVICE_REGISTRY,
        get_service_class,
        get_all_scopes,
        get_all_roles,
    )

    # Get a service config class
    RekuestConfig = get_service_class("rekuest")

    # Get all scopes from enabled services
    scopes = get_all_scopes(config)
"""

from typing import Dict, Type

from arkitekt_next.server.services.base import (
    BaseServiceConfig,
    ServiceProtocol,
    ServiceRole,
    ServiceScope,
)
from arkitekt_next.server.services.alpaka import AlpakaConfig
from arkitekt_next.server.services.elektro import ElektroConfig
from arkitekt_next.server.services.fluss import FlussConfig
from arkitekt_next.server.services.kabinet import KabinetConfig
from arkitekt_next.server.services.kraph import KraphConfig
from arkitekt_next.server.services.lok import LokConfig
from arkitekt_next.server.services.lovekit import LovekitConfig
from arkitekt_next.server.services.mikro import MikroConfig
from arkitekt_next.server.services.rekuest import RekuestConfig


# Service Registry - Maps service identifiers to their config classes
SERVICE_REGISTRY: Dict[str, Type[BaseServiceConfig]] = {
    "rekuest": RekuestConfig,
    "mikro": MikroConfig,
    "fluss": FlussConfig,
    "kabinet": KabinetConfig,
    "lok": LokConfig,
    "kraph": KraphConfig,
    "elektro": ElektroConfig,
    "alpaka": AlpakaConfig,
    "lovekit": LovekitConfig,
}


def get_service_class(identifier: str) -> Type[BaseServiceConfig] | None:
    """Get the service config class by identifier.

    Args:
        identifier: Service identifier (e.g., "rekuest", "mikro")

    Returns:
        Service config class or None if not found.
    """
    return SERVICE_REGISTRY.get(identifier)


def get_available_services() -> list[str]:
    """Get list of all available service identifiers."""
    return list(SERVICE_REGISTRY.keys())


def get_service_info(identifier: str) -> dict | None:
    """Get service metadata by identifier.

    Args:
        identifier: Service identifier

    Returns:
        Dict with name, description, roles, and scopes, or None if not found.
    """
    service_class = SERVICE_REGISTRY.get(identifier)
    if not service_class:
        return None

    return {
        "identifier": service_class.get_identifier(),
        "name": service_class.get_name(),
        "description": service_class.get_description(),
        "roles": [r.model_dump() for r in service_class.get_roles()],
        "scopes": [s.model_dump() for s in service_class.get_scopes()],
    }


def get_all_roles() -> list[ServiceRole]:
    """Get all roles from all services (deduplicated by key)."""
    roles_dict: Dict[str, ServiceRole] = {}
    for service_class in SERVICE_REGISTRY.values():
        for role in service_class.get_roles():
            if role.key not in roles_dict:
                roles_dict[role.key] = role
    return list(roles_dict.values())


def get_all_scopes() -> Dict[str, str]:
    """Get all scopes from all services as a dict (key -> description).

    Returns:
        Dict mapping scope keys to their descriptions.
    """
    scopes: Dict[str, str] = {}
    for service_class in SERVICE_REGISTRY.values():
        for scope in service_class.get_scopes():
            if scope.key not in scopes:
                scopes[scope.key] = scope.description
    return scopes


def get_enabled_service_scopes(
    *,
    rekuest_enabled: bool = True,
    mikro_enabled: bool = True,
    fluss_enabled: bool = True,
    kabinet_enabled: bool = True,
    lok_enabled: bool = True,
    kraph_enabled: bool = True,
    elektro_enabled: bool = False,
    alpaka_enabled: bool = False,
    lovekit_enabled: bool = True,
) -> Dict[str, str]:
    """Get scopes only from enabled services.

    Args:
        *_enabled: Whether each service is enabled

    Returns:
        Dict mapping scope keys to descriptions for enabled services.
    """
    enabled_map = {
        "rekuest": rekuest_enabled,
        "mikro": mikro_enabled,
        "fluss": fluss_enabled,
        "kabinet": kabinet_enabled,
        "lok": lok_enabled,
        "kraph": kraph_enabled,
        "elektro": elektro_enabled,
        "alpaka": alpaka_enabled,
        "lovekit": lovekit_enabled,
    }

    scopes: Dict[str, str] = {}
    for identifier, enabled in enabled_map.items():
        if enabled:
            service_class = SERVICE_REGISTRY.get(identifier)
            if service_class:
                for scope in service_class.get_scopes():
                    if scope.key not in scopes:
                        scopes[scope.key] = scope.description
    return scopes


__all__ = [
    # Base classes
    "BaseServiceConfig",
    "ServiceProtocol",
    "ServiceRole",
    "ServiceScope",
    # Service configs
    "AlpakaConfig",
    "ElektroConfig",
    "FlussConfig",
    "KabinetConfig",
    "KraphConfig",
    "LokConfig",
    "LovekitConfig",
    "MikroConfig",
    "RekuestConfig",
    # Registry and helpers
    "SERVICE_REGISTRY",
    "get_service_class",
    "get_available_services",
    "get_service_info",
    "get_all_roles",
    "get_all_scopes",
    "get_enabled_service_scopes",
]
