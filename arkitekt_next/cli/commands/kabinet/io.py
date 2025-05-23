import datetime
import uuid
from arkitekt_next.utils import create_arkitekt_next_folder
import os
from typing import Optional, List, Dict
from arkitekt_next.cli.types import (
    Manifest,
)

from .types import (
    Build,
    BuildsConfigFile,
    Flavour,
    DeploymentsConfigFile,
)
from kabinet.api.schema import (
    InspectionInput,
    AppImageInput,
    DockerImageInput,
    ManifestInput,
)

import yaml
import json
import rich_click as click


def get_builds(selected_run: Optional[str] = None) -> Dict[str, Build]:
    """Will load the builds.yaml file and return a dictionary of builds

    Will load the builds.yaml file and return a dictionary of builds
    where the key is the build_id and the value is the build object.


    Returns
    -------
    Dict[str, Build]
        The loaded builds
    """
    path = create_arkitekt_next_folder()
    config_file = os.path.join(path, "builds.yaml")

    builds = {}

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = BuildsConfigFile(**yaml.safe_load(file))

            # We will only return the builds from the selected run
            selected_run = selected_run or config.latest_build_run

            builds = {
                build.build_id: build
                for build in config.builds
                if build.build_run == selected_run
            }
            return builds
    else:
        raise click.ClickException(
            "Could not find any builds. Please run `arkitekt_next port build` first"
        )


def manifest_to_input(manifest: Manifest) -> ManifestInput:

    return ManifestInput(**manifest.model_dump(by_alias=True))


def generate_build(
    build_run: str,
    build_id: str,
    flavour_name: str,
    flavour: Flavour,
    manifest: Manifest,
    inspection: Optional[InspectionInput],
) -> Build:
    """Generates a build from a builder, build_id and manifest

    Will generate a build from a builder, build_id and manifest,
    and write it to the builds.yaml file in the arkitekt_next folder.


    Parameters
    ----------
    builder : str
        The builder that was used to build the build
    build_id : str
        The build_id of the build
    manifest : Manifest
        The manifest of the build

    Returns
    -------
    Build
        The generated build
    """
    path = create_arkitekt_next_folder()

    config_file = os.path.join(path, "builds.yaml")

    build = Build(
        manifest=manifest_to_input(manifest),
        flavour=flavour_name,
        selectors=flavour.selectors,
        build_id=build_id,
        build_run=build_run,
        description=flavour.description,
        inspection=inspection,
    )

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = BuildsConfigFile(**yaml.safe_load(file))
            config.builds.append(build)
            config.latest_build_run = build_run
    else:
        config = BuildsConfigFile(builds=[build], latest_build_run=build_run)

    with open(config_file, "w") as file:
        yaml.safe_dump(
            json.loads(
                config.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)
            ),
            file,
            sort_keys=True,
        )

    return build


def get_deployments() -> DeploymentsConfigFile:
    """Loads the deployments.yaml file and returns the deployments

    Will load the deployments.yaml file and return the deployments
    as a DeploymentsConfigFile object. If no deployments.yaml file
    exists, it will return an empty DeploymentsConfigFile object.

    Returns
    -------
    DeploymentsConfigFile
        The deployments as a DeploymentsConfigFile object
    """
    path = create_arkitekt_next_folder()
    config_file = os.path.join(path, "deployments.yaml")
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            return DeploymentsConfigFile(**yaml.safe_load(file))
    else:
        return DeploymentsConfigFile()


def generate_deployment(
    deployment_run: str,
    build: Build,
    image: str,
) -> AppImageInput:
    """Generates a deployment from a build and an image

    Parameters
    ----------

    build : Build
        The build that should be deployed
    image: str
        The image that is the actuall deployment of the build
    with_definitions: bool:
        Should we generated and inspect definitions to bundle with
        the deployment?

    Returns:
    ------
    Deployment: The created deployment

    """

    path = create_arkitekt_next_folder()

    config_file = os.path.join(path, "deployments.yaml")

    app_image = AppImageInput(
        appImageId=uuid.uuid4().hex,
        manifest=build.manifest,
        flavourName=build.flavour,
        selectors=build.selectors,
        inspection=build.inspection,
        image=DockerImageInput(imageString=image, buildAt=datetime.datetime.now()),
    )

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = DeploymentsConfigFile(**yaml.safe_load(file))
            config.app_images.append(app_image)
            config.latest_app_image = app_image.app_image_id
    else:
        config = DeploymentsConfigFile(
            app_images=[app_image], latest_app_image=app_image.app_image_id
        )

    with open(config_file, "w") as file:
        yaml.safe_dump(
            json.loads(config.model_dump_json(exclude_none=True, by_alias=True)),
            file,
            sort_keys=True,
        )

    return app_image
