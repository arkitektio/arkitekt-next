from pydantic import BaseModel
from typing import Dict, Any
from arkitekt_next.bloks.services.name import NameService
from blok import blok, InitContext, Option, ExecutionContext
from blok.tree import YamlFile
from arkitekt_next.bloks.services.secret import SecretService
import secrets
import namegenerator


@blok(NameService, description="Preformed names that will not change")
class PreformedNamesBlok:
    def __init__(self) -> None:
        self.preformed_names = [namegenerator.gen() for _ in range(100)]
        self.used_names = []

    def preflight(self, init: InitContext, preformed_names: list[str]):
        self.preformed_names = list(preformed_names)
        self.used_names = []

    def retrieve_name(self) -> str:
        name = self.preformed_names.pop()
        self.used_names.append(name)
        return name

    def get_options(self):
        config_path = Option(
            subcommand="preformed_names",
            help="A list of preformed names",
            default=self.preformed_names,
            multiple=True,
        )

        return [config_path]
