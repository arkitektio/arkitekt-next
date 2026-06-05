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

from arkitekt_next.cli.vars import get_console, set_console, get_manifest, set_manifest, get_work_dir, set_work_dir
from arkitekt_next.cli.texts import LOGO, ERROR_EPILOGUE
from arkitekt_next.cli.docs import CLI_DOCS_BASE, help_epilog
from arkitekt_next.cli.commands.run.main import run
from arkitekt_next.cli.commands.gen.main import gen
from arkitekt_next.cli.commands.kabinet.main import kabinet
from arkitekt_next.cli.commands.init.main import init
from arkitekt_next.cli.commands.manifest.main import manifest
from arkitekt_next.cli.commands.inspect.main import inspect
from arkitekt_next.cli.commands.call.main import call
from arkitekt_next.cli.io import load_manifest
from arkitekt_next.utils import create_arkitekt_next_folder

click.rich_click.HEADER_TEXT = LOGO
click.rich_click.ERRORS_EPILOGUE = ERROR_EPILOGUE
click.rich_click.USE_RICH_MARKUP = True


@click.group(epilog=help_epilog(CLI_DOCS_BASE))
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

    if ctx.invoked_subcommand != "init":
        create_arkitekt_next_folder(base_dir=work_dir)

        manifest = load_manifest(base_dir=work_dir)
        if manifest:
            set_manifest(ctx, manifest)


cli.add_command(init, "init")
cli.add_command(run, "run")
cli.add_command(gen, "gen")
cli.add_command(kabinet, "kabinet")
cli.add_command(manifest, "manifest")
cli.add_command(inspect, "inspect")
cli.add_command(call, "call")

if __name__ == "__main__":
    cli()
