import rich_click as click
from arkitekt_next.cli.vars import get_console, get_manifest
import os
from rich.panel import Panel
import subprocess
import uuid
from arkitekt_next.cli.io import generate_build
from click import Context
from arkitekt_next.cli.types import Flavour, InspectionInput
import yaml
from typing import Dict, Optional
import json
from arkitekt_next.base_models import Requirement
from arkitekt_next.utils import create_arkitekt_next_folder
from rekuest_next.api.schema import TemplateInput


class InspectionError(Exception):
    pass


def build_flavour(flavour_name: str, flavour: Flavour) -> str:
    """Builds the flavour to docker

    Parameters
    ----------
    flavour : Flavour
        The flavour to build
    manifest : Manifest
        The manifest of the app

    Returns
    -------

    tag: str
        The tag of the built docker container

    """

    build_id = str(uuid.uuid4())

    relative_dir = ".arkitekt_next/flavours/{}/".format(flavour_name)

    command = flavour.generate_build_command(build_id, relative_dir)

    docker_run = subprocess.run(" ".join(command), shell=True)

    if docker_run.returncode != 0:
        raise click.ClickException("Could not build docker container")

    return build_id


def inspect_docker_container(build_id: str) -> InspectionInput:
    try:
        # Run 'docker inspect' with the container ID or name
        result = subprocess.run(
            ["docker", "inspect", build_id],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )

        # Parse the JSON output
        try:
            container_info = json.loads(result.stdout)
        except json.decoder.JSONDecodeError as e:
            combined_error = result.stdout + result.stderr
            raise InspectionError(
                f"Could not decode JSON output of docker inspect. {combined_error}"
            ) from e

        # Extract size information
        try:
            size = container_info[0][
                "Size"
            ]  # Size of files that have been written to the filesystem
            size_root_fs = container_info[0][
                "Size"
            ]  # Total size of all the files in the container
        except IndexError as e:
            raise InspectionError("Container not found or invalid JSON output") from e
        except KeyError as e:
            raise InspectionError(
                "Size information not found in the container details"
            ) from e

        return size, size_root_fs
    except subprocess.CalledProcessError as e:
        combined_error = e.stdout + e.stderr
        raise InspectionError(f"An error occurred: {e.stdout + e.stderr}") from e


def inspect_templates(build_id: str) -> list[TemplateInput]:
    try:
        # Run 'docker inspect' with the container ID or name
        result = subprocess.run(
            ["docker", "run", build_id, "arkitekt-next", "inspect", "templates", "-mr"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        # Parse the JSON output
        correct_part = result.stdout.split("--START_TEMPLATES--")[1].split(
            "--END_TEMPLATES--"
        )[0]

        try:
            output = json.loads(correct_part)
        except json.decoder.JSONDecodeError as e:
            combined_error = result.stdout + result.stderr
            raise InspectionError(
                f"Could not decode JSON output of docker inspect. {combined_error}"
            ) from e

        return list(output.values())
    except subprocess.CalledProcessError as e:
        combined_error = e.stdout + e.stderr

        if "No such command" in combined_error:
            raise InspectionError(
                "Could not find the command `arkitekt_next inspect definitions` in the container. Maybe"
                + "you forgot to install arkitekt_next in the container? "
            )

        raise InspectionError(f"An error occurred: {e.stdout + e.stderr}") from e


def inspect_requirements(build_id: str) -> Dict[str, Requirement]:
    try:
        # Run 'docker inspect' with the container ID or name
        result = subprocess.run(
            [
                "docker",
                "run",
                build_id,
                "arkitekt-next",
                "inspect",
                "requirements",
                "-mr",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        # Parse the JSON output
        correct_part = result.stdout.split("--START_REQUIREMENTS--")[1].split(
            "--END_REQUIREMENTS--"
        )[0]

        try:
            output = json.loads(correct_part)
        except json.decoder.JSONDecodeError as e:
            combined_error = result.stdout + result.stderr
            raise InspectionError(
                f"Could not decode JSON output of docker inspect. {combined_error}"
            ) from e

        return output
    except subprocess.CalledProcessError as e:
        combined_error = e.stdout + e.stderr

        if "No such command" in combined_error:
            raise InspectionError(
                "Could not find the command `arkitekt_next inspect definitions` in the container. Maybe"
                + "you forgot to install arkitekt_next in the container? "
            )

        raise InspectionError(f"An error occurred: {e.stdout + e.stderr}") from e


def inspect_build(build_id: str) -> InspectionInput:
    size, size_root_fs = inspect_docker_container(build_id)
    templates = inspect_templates(build_id)
    requirements = inspect_requirements(build_id)

    return InspectionInput(size=size, templates=templates, requirements=requirements)


def get_flavours(ctx: Context, select: Optional[str] = None) -> Dict[str, Flavour]:
    """Gets the flavours for this app"""

    arkitekt_next_folder = create_arkitekt_next_folder()

    flavours_folder = os.path.join(arkitekt_next_folder, "flavours")

    if not os.path.exists(flavours_folder):
        raise click.ClickException(
            "We could not find the flavours folder. Please run `arkitekt_next port init` first to create a buildable flavour"
        )

    flavours = {}

    for dir_name in os.listdir(flavours_folder):
        dir = os.path.join(flavours_folder, dir_name)
        if os.path.isdir(dir):
            if select is not None and select != dir_name:
                continue

            if os.path.exists(os.path.join(dir, "config.yaml")):
                with open(os.path.join(dir, "config.yaml")) as f:
                    valued = yaml.load(f, Loader=yaml.SafeLoader)
                try:
                    flavour = Flavour.model_validate(valued)
                    flavour.check_relative_paths(dir)
                    flavours[dir_name] = flavour

                except Exception as e:
                    get_console(ctx).print_exception()
                    raise click.ClickException(
                        f"Could not load flavour {dir_name} from {dir} ` config.yaml ` is invalid"
                    ) from e

    return flavours


@click.command()
@click.option(
    "--flavour",
    "-f",
    help="The flavour to build. By default all flavours are being built",
    default=None,
    required=False,
)
@click.option(
    "--no-inspect",
    "-n",
    help="Should we skip the inspection of the app?",
    is_flag=True,
    default=False,
)
@click.pass_context
def build(ctx: Context, flavour: str, no_inspect: bool) -> None:
    """Builds the arkitekt_next app to docker"""

    manifest = get_manifest(ctx)
    console = get_console(ctx)

    flavours = get_flavours(ctx, select=flavour)

    md = Panel(
        "Starting to Build Containers for App [bold]{}[/bold]".format(
            manifest.identifier
        ),
        subtitle="Selected Flavours: {}".format(", ".join(flavours.keys())),
    )
    console.print(md)

    build_run = str(uuid.uuid4())

    for key, flavour in flavours.items():
        md = Panel(
            "Building Flavour [bold]{}[/bold]".format(key),
            subtitle="This may take a while...",
            subtitle_align="right",
        )
        console.print(md)

        build_tag = build_flavour(key, flavour)

        inspection = None
        if not no_inspect:
            inspection = inspect_build(build_tag)

        generate_build(build_run, build_tag, key, flavour, manifest, inspection)

        md = Panel(
            "Built Flavour [bold]{}[/bold]".format(key),
            subtitle="Build ID: {}".format(build_run),
            subtitle_align="right",
        )

        console.print(md)
