from importlib.metadata import version
from pydantic import BaseModel, Field, field_validator
import datetime
from typing import List, Optional, Union, Literal, Dict
from enum import Enum
import semver
import uuid
from arkitekt_next.base_models import Requirement
from string import Formatter
import os

from kabinet.api.schema import AppImageInput, InspectionInput, SelectorInput, ManifestInput
from rekuest_next.api.schema import TemplateInput

ALLOWED_BUILDER_KEYS = [
    "tag",
    "dockerfile",
    "package_version",
]


class Framework(str, Enum):
    """Do we support other frameworks?"""

    VANILLA = "vanilla"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"


class Packager(str, Enum):
    CONDA = "conda"
    POETRY = "poetry"
    PIP = "pip"


class Manifest(BaseModel):
    identifier: str
    version: str
    author: str
    logo: Optional[str] = None
    entrypoint: str
    scopes: List[str]

    @field_validator("version", mode="before")
    def version_must_be_semver(cls, v) -> str:
        """Checks that the version is a valid semver version"""
        if isinstance(v, str):
            try:
                semver.VersionInfo.parse(v)
            except ValueError:
                raise ValueError("Version must be a valid semver version")
        return str(v)

    def to_console_string(self):
        return f"📦 {self.identifier} ({self.version}) by {self.author}"

    def to_builder_dict(self):
        return {
            "identifier": self.identifier,
            "version": self.version,
            "logo": self.logo,
            "scopes": self.scopes,
        }

    class Config:
        validate_assignment = True


class SelectorType(str, Enum):
    RAM = "ram"
    CPU = "cpu"
    GPU = "gpu"
    LABEL = "label"


class Flavour(BaseModel):
    selectors: List[SelectorInput]
    description: str = Field(default="")
    dockerfile: str = Field(default="Dockerfile")
    build_command: List[str] = Field(
        default_factory=lambda: [
            "docker",
            "build",
            "-t",
            "{tag}",
            "-f",
            "{dockerfile}",
            ".",
        ]
    )

    @field_validator("build_command", mode="before")
    def check_valid_template_name(cls, value):
        """Checks that the build_command templates are valid"""

        for v in value:
            for literal_text, field_name, format_spec, conversion in Formatter().parse(v):
                if field_name is not None:
                    assert (
                        field_name in ALLOWED_BUILDER_KEYS
                    ), f"Invalid template key {field_name}. Allowed keys are {ALLOWED_BUILDER_KEYS}"

        return value

    def generate_build_command(self, tag: str, relative_dir: str):
        """Generates the build command for this flavour"""

        dockerfile = os.path.join(relative_dir, self.dockerfile)

        return [v.format(tag=tag, dockerfile=dockerfile) for v in self.build_command]

    def check_relative_paths(self, flavour_folder: str):
        """Checks that the paths are relative to the flavour folder"""

        dockerfile_path = os.path.join(flavour_folder, self.dockerfile)

        if not os.path.exists(dockerfile_path):
            raise Exception(
                f"Could not find Dockerfile {self.dockerfile} in flavour {flavour_folder}"
            )



class DeploymentsConfigFile(BaseModel):
    """The ConfigFile is a pydantic model that represents the deployments.yaml file


    Parameters
    ----------
    BaseModel : _type_
        _description_
    """

    app_images: List[AppImageInput] = []
    latest_app_image: Optional[str] = None


class Build(BaseModel):
    build_run: str
    build_id: str
    inspection: Optional[InspectionInput] = None
    description: str = Field(default="")
    selectors: List[SelectorInput] = Field(default_factory=list)
    flavour: str = Field(default="vanilla")
    manifest: ManifestInput
    build_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    base_docker_command: List[str] = Field(
        default_factory=lambda: ["docker", "run", "-it", "--net", "host"]
    )
    base_arkitekt_next_command: List[str] = Field(
        default_factory=lambda: ["arkitekt-next", "run", "prod", "--headless"]
    )

    def build_docker_command(self) -> List[str]:
        """Builds the docker command for this build"""

        base_command = self.base_docker_command

        for selector in self.selectors:
            base_command = base_command + selector.build_docker_params()

        base_command = base_command + [self.build_id]

        return base_command

    def build_arkitekt_next_command(self, fakts_url: str):
        """Builds the arkitekt_next command for this build"""

        base_command = self.base_arkitekt_next_command

        for selector in self.selectors:
            base_command = base_command + selector.build_arkitekt_next_params()

        base_command = base_command + ["--url", fakts_url]

        return base_command


class BuildsConfigFile(BaseModel):
    builds: List[Build] = Field(default_factory=list)
    latest_build_run: Optional[str] = None
