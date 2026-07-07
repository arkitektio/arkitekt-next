import sys
import rich_click as click
from arkitekt_next.cli.vars import get_console, get_manifest, get_work_dir
import os
from rich.panel import Panel
import subprocess
import uuid

from kabinet.api.schema import RequirementInput
from .io import generate_build, get_flavours
from click import Context
from .types import Flavour, InspectionInput
import json
from typing import Any, Dict, List, Optional
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL


class InspectionError(Exception):
    pass


def build_flavour(flavour_name: str, flavour: Flavour, work_dir: str) -> str:
    """Builds a flavour to a Docker image and returns the build_id (tag)."""
    build_id = str(uuid.uuid4())
    relative_dir = os.path.join(".arkitekt_next", "flavours", flavour_name, "")
    command = flavour.generate_build_command(build_id, relative_dir)
    docker_run = subprocess.run(" ".join(command), shell=True, cwd=work_dir)
    if docker_run.returncode != 0:
        raise click.ClickException("Could not build docker container")
    return build_id


def inspect_docker_container(build_id: str) -> tuple[int, int]:
    try:
        result = subprocess.run(
            ["docker", "inspect", build_id],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        try:
            container_info = json.loads(result.stdout)
        except json.decoder.JSONDecodeError as e:
            raise InspectionError(
                f"Could not decode JSON output of docker inspect. {result.stdout}"
            ) from e
        try:
            size = container_info[0]["Size"]
            size_root_fs = container_info[0]["Size"]
        except (IndexError, KeyError) as e:
            raise InspectionError("Size information not found in container details") from e
        return size, size_root_fs
    except subprocess.CalledProcessError as e:
        raise InspectionError(f"An error occurred: {e.stdout}{e.stderr}") from e


def inspect_all(build_id: str, url: str) -> Dict[str, Any]:
    try:
        process = subprocess.Popen(
            " ".join([
                "docker", "run", "-it", "--network", "host",
                build_id, "arkitekt-next", "inspect", "all", "-mr",
            ]),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        lines: list[str] = []
        while True:
            if process.poll() is not None:
                break
            nextline = process.stdout.readline()
            lines.append(nextline.decode("utf-8"))
            sys.stdout.buffer.write(nextline)
            sys.stdout.flush()

        process.communicate()
        result = "\n".join(lines)

        if process.returncode != 0:
            if "ModuleNotFoundError" in result:
                raise click.ClickException(
                    "Missing a module in the container. Make sure all dependencies are installed."
                )
            raise click.ClickException(
                "Running `arkitekt-next inspect all` inside the container failed."
            )

        correct_part = result.split("--START_AGENT--")[1].split("--END_AGENT--")[0]
        try:
            return json.loads(correct_part)
        except json.decoder.JSONDecodeError as e:
            raise InspectionError(f"Could not decode inspection JSON. {result}") from e

    except subprocess.CalledProcessError as e:
        combined = e.stdout + e.stderr
        if "No such command" in combined:
            raise InspectionError(
                "Command `arkitekt-next inspect implementations` not found in container. "
                "Did you forget to install arkitekt-next?"
            )
        raise InspectionError(f"An error occurred: {combined}") from e


def inspect_requirements(build_id: str) -> List[RequirementInput]:
    try:
        result = subprocess.run(
            ["docker", "run", build_id, "arkitekt-next", "inspect", "requirements", "-mr"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        correct_part = result.stdout.split("--START_REQUIREMENTS--")[1].split(
            "--END_REQUIREMENTS--"
        )[0]
        try:
            return json.loads(correct_part)
        except json.decoder.JSONDecodeError as e:
            raise InspectionError(
                f"Could not decode requirements JSON. {result.stdout + result.stderr}"
            ) from e
    except subprocess.CalledProcessError as e:
        combined = e.stdout + e.stderr
        if "No such command" in combined:
            raise InspectionError(
                "Command `arkitekt-next inspect requirements` not found in container."
            )
        raise InspectionError(f"An error occurred: {combined}") from e


def inspect_build(build_id: str, url: str) -> InspectionInput:
    size, size_root_fs = inspect_docker_container(build_id)
    runtime = inspect_all(build_id, url)
    print("Runtime inspection result:", runtime)
    return InspectionInput(size=size, **runtime)


@click.command()
@click.option(
    "--flavour", "-f",
    help="The flavour to build. By default all flavours are built.",
    default=None,
    required=False,
)
@click.option(
    "--no-inspect", "-n",
    help="Skip inspection of the app.",
    is_flag=True,
    default=False,
)
@click.option(
    "--tag", "-t",
    help="Tag the build with a specific tag.",
    type=str,
    default=None,
    required=False,
)
@click.option(
    "--url", "-u",
    help="The fakts-next server to use.",
    type=str,
    default=DEFAULT_ARKITEKT_URL,
)
@click.pass_context
def build(ctx: Context, flavour: str, no_inspect: bool, tag: Optional[str], url: str) -> None:
    """Builds the arkitekt-next app to Docker."""
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    work_dir = get_work_dir(ctx)

    flavours = get_flavours(base_dir=work_dir, select=flavour)

    console.print(Panel(
        "Starting to Build Containers for App [bold]{}[/bold]".format(manifest.identifier),
        subtitle="Selected Flavours: {}".format(", ".join(flavours.keys())),
    ))

    build_run = str(uuid.uuid4())

    for key, inspected_flavour in flavours.items():
        console.print(Panel(
            "Building Flavour [bold]{}[/bold]".format(key),
            subtitle="This may take a while...",
            subtitle_align="right",
        ))

        build_tag = build_flavour(key, inspected_flavour, work_dir)

        if tag:
            subprocess.run(["docker", "tag", build_tag, tag], check=True)

        inspection = None
        if not no_inspect:
            inspection = inspect_build(build_tag, url)

        generate_build(build_run, build_tag, key, inspected_flavour, manifest, inspection, base_dir=work_dir)

        console.print(Panel(
            "Built Flavour [bold]{}[/bold]".format(key),
            subtitle="Build ID: {}".format(build_run),
            subtitle_align="right",
        ))
