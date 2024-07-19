from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, CLIOption, ExecutionContext
from blok.tree import YamlFile


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok("live.arkitekt.config")
class ConfigBlok:
    def __init__(self) -> None:
        self.config_path = "configs"
        self.registered_configs = {}

    def init(self, init: InitContext):
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
        config_path = CLIOption(
            subcommand="config_path",
            help="Which path to use for configs",
            default=self.config_path,
            show_default=True,
        )

        return [config_path]
