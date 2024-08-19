from pydantic import BaseModel
from typing import Dict, Any
from arkitekt_next.bloks.services.mount import MountService
from blok import blok, InitContext, Option, ExecutionContext

from blok.tree import YamlFile


@blok(MountService, description="Mounting files into the file tree for use")
class MountBlok:
    def __init__(self) -> None:
        self.mount_path = "mounts"
        self.registered_configs = {}

    def preflight(self, mount_path: str):
        self.mount_path = mount_path

    def build(self, ex: ExecutionContext):
        for name, file in self.registered_configs.items():
            ex.file_tree.set_nested(*f"{self.mount_path}/{name}".split("/"), file)

    def register_mount(self, name: str, file: YamlFile) -> str:
        self.registered_configs[name] = file
        return f"./{self.mount_path}/" + name

    def get_options(self):
        config_path = Option(
            subcommand="mount_path",
            help="Which path to use for configs",
            default=self.mount_path,
            show_default=True,
        )

        return [config_path]
