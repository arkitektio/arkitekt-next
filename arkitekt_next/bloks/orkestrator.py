from typing import Dict, Any
import secrets
from arkitekt_next.bloks.services.mount import MountService
from blok import blok, InitContext, ExecutionContext, Option, Command
from blok.bloks.services.vscode import VsCodeService
from blok.tree import Repo, YamlFile


@blok(
    "live.arkitekt.orkestrator",
    description="Orkestrator is the electron-based UI for arkitekt",
)
class OrkestratorBlok:
    def __init__(self) -> None:
        self.dev = False
        self.disable = True
        self.repo = "https://github.com/arkitektio/orkestrator-next"
        self.build_command = ["yarn"]
        self.up_command = ["yarn", "start"]

    def preflight(
        self,
        init: InitContext,
        mount: MountService,
        vscode: VsCodeService | None = None,
    ):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        if self.disable and not self.dev:
            return
        self.mount = mount.register_mount("orkestrator", Repo(self.repo))

        if vscode is not None:
            vscode.register_task(
                "Run Orkestrator",
                "shell",
                "yarn",
                ["start"],
                {"cwd": f"{self.mount}"},
            )
            vscode.register_task(
                "Build Orkestrator",
                "shell",
                "yarn",
                [],
                {"cwd": f"{self.mount}"},
            )

        self.initialized = True

    def build(self, context: ExecutionContext):
        if self.disable and not self.dev:
            return

        context.install_commands.set_nested(
            "orkestrator", Command(self.build_command, cwd=self.mount)
        )
        context.up_commands.set_nested(
            "orkestrator", Command(self.up_command, cwd=self.mount)
        )
        pass

    def get_options(self):
        with_repos = Option(
            subcommand="repo",
            help="The default repo to use for the orkestrator",
            default=self.repo,
        )
        with_disable = Option(
            subcommand="disable",
            help="Should we disable the orkestrator service?",
            default=self.disable,
        )
        with_dev = Option(
            subcommand="dev",
            help="Should we mount orkestrator as dev?",
            default=self.dev,
        )

        return [
            with_dev,
            with_repos,
            with_disable,
        ]
