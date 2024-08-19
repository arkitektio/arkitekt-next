from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Option, ExecutionContext
from blok.tree import YamlFile
from arkitekt_next.bloks.services.secret import SecretService
import secrets


@blok(SecretService, description="Preformed secrets that will not change")
class SecretBlok:
    def __init__(self) -> None:
        self.preformed_secrets = [secrets.token_urlsafe(32) for _ in range(100)]
        self.registered_secrets = []

    def preflight(self, init: InitContext, preformed_secrets: list[str]):
        self.preformed_secrets = list(preformed_secrets)

    def retrieve_secret(self) -> str:
        new_secret = self.preformed_secrets.pop()
        self.registered_secrets.append(new_secret)
        return new_secret

    def get_options(self):
        config_path = Option(
            subcommand="preformed_secrets",
            help="Which path to use for configs",
            default=self.preformed_secrets,
            multiple=True,
            show_default=False,
        )

        return [config_path]
