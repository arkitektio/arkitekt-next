"""Shared helpers for the server-deployment CLI groups (`hub`, `coord`, `hubinator`).

Each group drives the migrated ``arkitekt_next.server`` library but now with its
OWN deep, standalone profile schema and its OWN config file:

- ``hub``       -> ``HubConfig``            -> ``hub_config.yaml``       -> ``write_hub_files``
- ``coord``     -> ``CoordConfig``          -> ``coord_config.yaml``     -> ``write_coord_files``
- ``hubinator`` -> ``ArkitektServerConfig`` -> ``hubinator_config.yaml`` -> ``write_virtual_config_files``

An ``init`` command writes the profile to YAML; an ``up`` command regenerates the
docker-compose stack (services + auth wiring) from it and runs ``docker compose up``.
The YAML writing and the compose/up flow are shared here and parameterized by the
(filename, schema, generator) triple.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Callable, Type

import rich_click as click
from pydantic import BaseModel

from arkitekt_next.cli.vars import get_console, get_work_dir

#: Per-profile on-disk config filenames.
HUB_CONFIG_FILENAME = "hub_config.yaml"
COORD_CONFIG_FILENAME = "coord_config.yaml"
HUBINATOR_CONFIG_FILENAME = "hubinator_config.yaml"
ENGINE_CONFIG_FILENAME = "engine_config.yaml"


def resolve_path(ctx, path: str | None) -> Path:
    """Resolve the deployment directory: the positional ``path`` if given, else
    the global ``--work-dir``."""
    if path is None:
        return Path(get_work_dir(ctx))
    return Path(os.path.abspath(path))


def set_enabled_services(config, services) -> None:
    """Enable exactly ``services`` (an iterable of identifiers) and disable the rest.

    Only applies to profiles that carry data/compute service fields (hub /
    hubinator). ``lok`` is never toggled here.
    """
    from arkitekt_next.server.services import SERVICE_REGISTRY

    wanted = set(services)
    unknown = wanted - set(SERVICE_REGISTRY)
    if unknown:
        raise click.ClickException(
            f"Unknown service(s): {', '.join(sorted(unknown))}. "
            f"Available: {', '.join(sorted(SERVICE_REGISTRY))}"
        )
    for name in SERVICE_REGISTRY:
        if name == "lok" or not hasattr(config, name):
            continue
        getattr(config, name).enabled = name in wanted


def write_profile(
    ctx, path: Path, config: BaseModel, *, filename: str, kind: str, backend: str = "docker"
) -> Path:
    """Write ``config`` to ``<path>/<filename>`` under the versioned profile wrapper."""
    from arkitekt_next.server.utils import write_profile_yaml

    path.mkdir(parents=True, exist_ok=True)
    config_path = path / filename
    write_profile_yaml(str(config_path), config, kind=kind, backend=backend)
    get_console(ctx).print(
        f"[bold green]✓[/bold green] Wrote configuration to [cyan]{config_path}[/cyan]"
    )
    return config_path


def compose_and_up(
    ctx,
    path: Path,
    *,
    filename: str,
    model_cls: Type[BaseModel],
    generator: Callable[[Path, Any], None],
) -> None:
    """Load a profile config, regenerate the compose/config files, then ``docker compose up``."""
    from arkitekt_next.server.runner import compose_up
    from arkitekt_next.server.utils import load_profile_yaml

    console = get_console(ctx)
    config_path = path / filename
    try:
        config, _backend = load_profile_yaml(str(config_path), model_cls)
    except FileNotFoundError:
        raise click.ClickException(
            f"No configuration found at {config_path}. Run the matching `init` command first."
        )

    console.print("[blue]Composing deployment (services + auth wiring)...[/blue]")
    generator(path, config)

    # Docker is only required for `up` — generation above already succeeded, so if
    # Docker is missing we point the user at the ready-to-run files instead of failing
    # opaquely.
    if not shutil.which("docker"):
        raise click.ClickException(
            "Docker is not installed, but it is required to start the stack with `up`.\n"
            "The deployment files were generated in "
            f"{path} — install Docker (https://docs.docker.com/get-docker/) and run "
            "`docker compose up` there, or re-run this command."
        )

    console.print("[blue]Starting the stack with `docker compose up`...[/blue]")
    try:
        compose_up(path)
    except Exception as e:  # pragma: no cover - surfaced to the user
        raise click.ClickException(
            f"Failed to start the stack (is Docker running?): {e}"
        )
    console.print("[bold green]✓ Deployment is up.[/bold green]")
