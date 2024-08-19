from pydantic import BaseModel
from typing import Dict, Any
from blok import blok, InitContext, Option
from arkitekt_next.bloks.services.admin import AdminService, AdminCredentials


@blok(AdminService, description="sdmin credentials for the application")
class AdminBlok:
    def __init__(self) -> None:
        self.password = "admin"
        self.username = "admin"
        self.email = "admin@admin.com"

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def retrieve(self):
        return AdminCredentials(
            password=self.password,
            username=self.username,
            email=self.email,
        )

    def get_options(self):
        with_username = Option(
            subcommand="username",
            help="Which admin username to use",
            default=self.username,
            show_default=True,
        )
        with_username = Option(
            subcommand="password",
            help="Which password to use",
            default=self.password,
            show_default=True,
        )
        with_email = Option(
            subcommand="password",
            help="Which password to use",
            default=self.password,
            show_default=True,
        )

        return [with_username, with_username, with_email]
