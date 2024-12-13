import os
from arkitekt_next.base_models import Manifest
import json


def create_arkitekt_next_folder(with_cache: bool = True) -> str:
    """Creates the .arkitekt_next folder in the current directory.

    If the folder already exists, it does nothing.
    It automatically creates a .gitignore file, and a .dockerignore file,
    so that the ArkitektNext credential files are not added to git.

    Parameters
    ----------
    with_cache : bool, optional
        Should we create a cache dir?, by default True

    Returns
    -------
    str
        The path to the .arkitekt_next folder.
    """
    os.makedirs(".arkitekt_next", exist_ok=True)
    if with_cache:
        os.makedirs(".arkitekt_next/cache", exist_ok=True)

    gitignore = os.path.join(".arkitekt_next", ".gitignore")
    dockerignore = os.path.join(".arkitekt_next", ".dockerignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w") as f:
            f.write(
                "# Hiding ArkitektNext Credential files from git\n*.json\n*.temp\ncache/\nservers/"
            )
    if not os.path.exists(dockerignore):
        with open(dockerignore, "w") as f:
            f.write(
                "# Hiding ArkitektNext Credential files from git\n*.json\n*.temp\ncache/\nservers/"
            )

    return os.path.abspath(".arkitekt_next")


def create_devcontainer_file(
    manifest: Manifest,
    flavour: str,
    docker_file_path,
    devcontainer_path=".devcontainer",
) -> None:
    """Creates a devcontainer.json file in the flavour folder.

    Parameters
    ----------
    flavour_folder : str
        The path to the flavour folder.
    """

    os.makedirs(devcontainer_path, exist_ok=True)

    flavour_container = os.path.join(devcontainer_path, flavour)
    os.makedirs(flavour_container, exist_ok=True)

    devcontainer_file = os.path.join(flavour_container, "devcontainer.json")

    devcontainer_content = {}
    devcontainer_content["name"] = f"{manifest.identifier} {flavour} Devcontainer"
    devcontainer_content["build"] = {}
    devcontainer_content["build"]["dockerfile"] = os.path.relpath(
        docker_file_path, flavour_container
    )
    devcontainer_content["build"][
        "context"
    ] = "../.."  # This is the root of the project
    devcontainer_content["runArgs"] = ["--network=host"]

    json.dump(devcontainer_content, open(devcontainer_file, "w"), indent=4)
