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

from arkitekt_next.cli.vars import *
from arkitekt_next.cli.constants import *
from arkitekt_next.cli.texts import *
from arkitekt_next.cli.commands.run.main import run
from arkitekt_next.cli.commands.gen.main import gen
from arkitekt_next.cli.commands.kabinet.main import kabinet
from arkitekt_next.cli.commands.init.main import init
from arkitekt_next.cli.commands.manifest.main import manifest
from arkitekt_next.cli.commands.inspect.main import inspect
from arkitekt_next.cli.commands.call.main import call
from arkitekt_next.cli.io import load_manifest
from arkitekt_next.utils import create_arkitekt_next_folder

default_docker_file = """
FROM python:3.8-slim-buster


RUN pip install arkitekt_next==0.4.23


RUN mkdir /app
COPY . /app
WORKDIR /app

"""


click.rich_click.HEADER_TEXT = LOGO
click.rich_click.ERRORS_EPILOGUE = ERROR_EPILOGUE
click.rich_click.USE_RICH_MARKUP = True


@click.group()
@click.pass_context
def cli(ctx):
    """ArkitektNext is a framework for building safe and performant apps that then can be centrally orchestrated and managed
    in workflows.


    This is the CLI for the ArkitektNext Python SDK. It allows you to create and deploy ArkitektNext Apps from your python code
    as well as to run them locally for testing and development. For more information about ArkitektNext, please visit
    [link=https://arkitekt.live]https://arkitekt.live[/link]
    """
    sys.path.append(os.getcwd())

    ctx.obj = {}
    console = Console()
    set_console(ctx, console)

    create_arkitekt_next_folder()

    manifest = load_manifest()
    if manifest:
        set_manifest(ctx, manifest)

    pass


cli.add_command(init, "init")
cli.add_command(run, "run")
cli.add_command(gen, "gen")
cli.add_command(kabinet, "kabinet")
cli.add_command(manifest, "manifest")
cli.add_command(inspect, "inspect")
cli.add_command(call, "call")

if __name__ == "__main__":
    cli()
