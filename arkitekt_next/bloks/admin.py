from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, CLIOption


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok("live.arkitekt.admin")
class AdminBlok:
    def __init__(self) -> None:
        self.password = "admin"
        self.username = "admin"
        self.email = "admin@admin.com"

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, cwd):
        pass

    def retrieve(self):
        return AdminCredentials(
            password=self.password,
            username=self.username,
            email=self.email,
        )

    def get_options(self):
        with_username = CLIOption(
            subcommand="username",
            help="Which admin username to use",
            default=self.username,
            show_default=True,
        )
        with_username = CLIOption(
            subcommand="password",
            help="Which password to use",
            default=self.password,
            show_default=True,
        )
        with_email = CLIOption(
            subcommand="password",
            help="Which password to use",
            default=self.password,
            show_default=True,
        )

        return [with_username, with_username, with_email]
