"""Docker-compose lifecycle helpers for generated Arkitekt deployments.

Migrated from ``arkitekt_server/commands/core.py`` and stripped of the Typer
command layer. These are plain functions the CLI (``cli/commands/hub|coord|
hubinator``) calls after generating the compose/config files via
:func:`arkitekt_next.server.dev.create_server`.
"""

import subprocess
from pathlib import Path


def run_command_in_directory(command: str, directory: Path | str) -> subprocess.CompletedProcess:
    """Run a shell command in a specific directory, raising on non-zero exit."""
    return subprocess.run(command, shell=True, cwd=str(directory), check=True)


def compose_up(directory: Path | str, *, detach: bool = True) -> None:
    """Run ``docker compose up`` in the given directory."""
    command = "docker compose up -d" if detach else "docker compose up"
    run_command_in_directory(command, directory)


def compose_pull(directory: Path | str) -> None:
    """Pull the latest images referenced by the compose file."""
    run_command_in_directory("docker compose pull", directory)


def compose_down(directory: Path | str) -> None:
    """Stop and remove the compose deployment in the given directory."""
    run_command_in_directory("docker compose down", directory)
