import sys
import os

try:
    import rich_click as click

    from rich.console import Console
except ImportError:
    print(
        "ArkitektNext CLI is not installed, please install it first. By installing the cli, e.g with `pip install arkitekt_next[cli]`, you can use the `arkitekt_next` command."
    )
    sys.exit(1)

from arkitekt_next.cli.vars import set_console, set_work_dir
from arkitekt_next.cli.texts import LOGO, ERROR_EPILOGUE
from arkitekt_next.cli.docs import CLI_DOCS_BASE, help_epilog
from arkitekt_next.cli.commands.app.main import app
from arkitekt_next.cli.commands.hub.main import hub
from arkitekt_next.cli.commands.coord.main import coord
from arkitekt_next.cli.commands.hubinator.main import hubinator
from arkitekt_next.cli.commands.engine.main import engine
from arkitekt_next.cli.commands.self.main import self_group
from arkitekt_next.cli.commands.plugin.main import plugin

click.rich_click.HEADER_TEXT = LOGO
click.rich_click.ERRORS_EPILOGUE = ERROR_EPILOGUE
click.rich_click.TEXT_MARKUP = "rich"

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(epilog=help_epilog(CLI_DOCS_BASE), context_settings=CONTEXT_SETTINGS)
@click.option(
    "--work-dir",
    "-w",
    default=".",
    type=click.Path(),
    help="Working directory for the app. Defaults to the current directory.",
    is_eager=True,
)
@click.pass_context
def cli(ctx, work_dir):
    """ArkitektNext is a framework for building safe and performant apps that then can be centrally orchestrated and managed
    in workflows.


    This is the CLI for the ArkitektNext Python SDK. It allows you to create and deploy ArkitektNext Apps from your python code
    as well as to run them locally for testing and development. For more information about ArkitektNext, please visit
    [link=https://arkitekt.live]https://arkitekt.live[/link]
    """
    work_dir = os.path.abspath(work_dir)
    sys.path.insert(0, work_dir)

    ctx.obj = {}
    console = Console()
    set_console(ctx, console)
    set_work_dir(ctx, work_dir)

    # The manifest/`.arkitekt_next` folder is only relevant to the `app` command
    # group (the client SDK). It is loaded lazily inside that group's callback so
    # the server-deployment groups (`hub`/`coord`/`hubinator`) don't require an
    # app project in the working directory.


cli.add_command(app, "app")
cli.add_command(hub, "hub")
cli.add_command(coord, "coord")
cli.add_command(hubinator, "hubinator")
cli.add_command(engine, "engine")
cli.add_command(self_group, "self")
cli.add_command(plugin, "plugin")

if __name__ == "__main__":
    cli()
