from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Option, ExecutionContext
from blok.tree import YamlFile
from arkitekt_next.bloks.services.config import ConfigService


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok(ConfigService)
class ConfigBlok:
    def __init__(self) -> None:
        self.config_path = "configs"
        self.registered_configs = {}

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, ex: ExecutionContext):
        for name, file in self.registered_configs.items():
            ex.file_tree.set_nested(*f"{self.config_path}/{name}".split("/"), file)

    def register_config(self, name: str, file: YamlFile) -> str:
        self.registered_configs[name] = file
        return f"./{self.config_path}/" + name

    def get_path(self, name: str) -> str:
        return f"./{self.config_path}/" + name

    def get_options(self):
        config_path = Option(
            subcommand="config_path",
            help="Which path to use for configs",
            default=self.config_path,
            show_default=True,
        )

        return [config_path]
