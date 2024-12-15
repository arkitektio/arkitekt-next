import datetime
import uuid
from arkitekt_next.utils import create_arkitekt_next_folder
import os
from typing import Optional, List, Dict
from arkitekt_next.cli.types import (
    Manifest,
)
import yaml
import json
import rich_click as click


def load_manifest_yaml(path: str) -> Manifest:
    """Loads a manifest from a yaml file

    Uses yaml safe load to load the manifest from a yaml file
    (to avoid unsafe yaml attributes)

    Parameters
    ----------
    path : str
        The path to the yaml file

    Returns
    -------
    Manifest
        The loaded manifest
    """
    with open(path, "r") as file:
        manifest = yaml.safe_load(file)
        return Manifest(**manifest)


def load_manifest() -> Optional[Manifest]:
    """Loads the manifest from the arkitekt_next folder

    Will load the manifest from the current working directories
    arkitekt_next folder. If no folder exists, it will create one, but
    will not create a manifest.

    Returns
    -------
    Optional[Manifest]
        The loaded manifest, or None if no manifest exists
    """
    path = create_arkitekt_next_folder()
    config_file = os.path.join(path, "manifest.yaml")
    if os.path.exists(config_file):
        return load_manifest_yaml(config_file)
    return None


def write_manifest(manifest: Manifest):
    """Writes a manifest to the arkitekt_next folder

    Will write a manifest to the current working directories
    arkitekt_next folder. If no folder exists, it will create one.


    Parameters
    ----------
    manifest : Manifest
        The manifest to write
    """
    path = create_arkitekt_next_folder()
    config_file = os.path.join(path, "manifest.yaml")

    with open(config_file, "w") as file:
        yaml.safe_dump(
            json.loads(manifest.json(exclude_none=True, exclude_unset=True)),
            file,
            sort_keys=True,
        )
