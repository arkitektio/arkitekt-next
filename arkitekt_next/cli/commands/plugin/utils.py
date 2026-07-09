import logging
from typing import Optional
import os
import yaml
from .types import Flavour
from arkitekt_next.cli.vars import get_console
import rich_click as click


def search_username_in_docker_info(docker_info: str):
    for line in docker_info.splitlines():
        if "Username" in line:
            return line.split(":")[1].strip()


def validate_flavours(flavours_folder: str, only: Optional[str]):
    for dir_name in os.listdir(flavours_folder):
        dir = os.path.join(flavours_folder, dir_name)
        if os.path.isdir(dir):
            if only is not None and only != dir_name:
                continue

            if os.path.exists(os.path.join(dir, "config.yaml")):
                with open(os.path.join(dir, "config.yaml")) as f:
                    valued = yaml.load(f, Loader=yaml.SafeLoader)
                try:
                    flavour = Flavour(**valued)

                except Exception as e:
                    get_console().print_exception()
                    raise click.ClickException(f"Flavour {dir_name} is invalid") from e

                try:
                    flavour.check_relative_paths(dir)
                except Exception as e:
                    raise click.ClickException(
                        f"Relative Paths in Flavour {dir_name} are invalid. {e}"
                    ) from e

            else:
                raise click.ClickException(
                    f"Flavour {dir_name} is invalid. No config.yaml file found"
                )

        else:
            logging.info(
                f"Found file {dir_name} in flavours folder. Not a valid flavour. Ignoring"
            )
