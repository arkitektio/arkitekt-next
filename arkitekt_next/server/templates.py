"""Configuration templates for Arkitekt server deployments.

Migrated from ``arkitekt_server/commands/init.py`` (the Typer command layer).
These are framework-agnostic helpers that mutate an :class:`ArkitektServerConfig`
into a named flavour. The CLI command layer (``cli/commands/hub|coord|hubinator``)
selects one of these by the ``--template`` option.
"""

from typing import TypeVar

from arkitekt_next.server.config import ArkitektServerConfig

#: The templates a ``--template`` option may select.
TEMPLATES = ["stable", "dev", "default", "minimal"]

# Any of the deployment-profile schemas (hubinator / hub / coord). The template
# builders only touch service fields that are present, so they are schema-agnostic.
C = TypeVar("C")

#: Stable-channel image pins, applied to whichever of these services the profile has.
_STABLE_IMAGES = {
    "mikro": "jhnnsrs/mikro:next",
    "fluss": "jhnnsrs/fluss:next",
    "elektro": "jhnnsrs/elektro:next",
    "alpaka": "jhnnsrs/alpaka:next",
    "lok": "jhnnsrs/lok:next",
    "rekuest": "jhnnsrs/rekuest:next",
}

#: Services that get built from a mounted GitHub checkout in the dev template.
_DEV_SERVICES = ["rekuest", "mikro", "fluss", "elektro", "lok", "alpaka"]


def create_stable_config(config: C) -> C:
    """Pin every present service to the ``next`` channel (schema-agnostic)."""
    for name, image in _STABLE_IMAGES.items():
        service = getattr(config, name, None)
        if service is not None:
            service.image = image
    return config


def create_dev_config(config: C) -> C:
    """Build every present service from a mounted GitHub checkout (schema-agnostic)."""
    for name in _DEV_SERVICES:
        service = getattr(config, name, None)
        if service is not None:
            service.mount_github = True
    return config


def create_minimal_config(config: C) -> C:
    """Create a minimal configuration for Arkitekt server."""
    # Minimal config logic here if needed
    return config


def create_default_config(config: C) -> C:
    """Create a default configuration for Arkitekt server."""
    # Default config logic here if needed
    return config


def apply_template(config: C, template: str) -> C:
    """Apply a named template to a config, raising ``ValueError`` on an unknown name."""
    builders = {
        "stable": create_stable_config,
        "dev": create_dev_config,
        "minimal": create_minimal_config,
        "default": create_default_config,
    }
    try:
        builder = builders[template]
    except KeyError:
        raise ValueError(
            f"Unknown template: {template}. Available templates: {', '.join(TEMPLATES)}"
        )
    return builder(config)
