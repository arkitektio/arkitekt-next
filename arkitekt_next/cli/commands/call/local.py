import rich_click as click
from arkitekt_next.cli.options import *
import asyncio
from arkitekt_next.cli.ui import construct_run_panel
from importlib import import_module
from arkitekt_next.cli.utils import import_builder
from rekuest_next.api.schema import NodeKind, BindsInput
from rich.table import Table
from rich.console import Console
from typing import Dict, Any


async def call_app(
    console: Console,
    app: App,
    template_string: str,
    arg: Dict[str, Any],
):
    async with app:
        raise NotImplementedError("Not implemented yet")


@click.command("prod")
@click.option(
    "--url",
    help="The fakts url for connection",
    default=DEFAULT_ARKITEKT_URL,
    envvar="FAKTS_URL",
)
@with_builder
@with_token
@with_instance_id
@with_headless
@with_log_level
@with_skip_cache
@click.pass_context
@click.option(
    "--arg",
    "-a",
    "args",
    help="Key Value pairs for the setup",
    type=(str, str),
    multiple=True,
)
@click.option(
    "--template",
    "-t",
    "template",
    help="The template to run",
    type=str,
)
def local(
    ctx,
    entrypoint=None,
    builder=None,
    args=None,
    template: str = None,
    **builder_kwargs,
):
    """Runs the app in production mode

    \n
    You can specify the builder to use with the --builder flag. By default, the easy builder is used, which is designed to be easy to use and to get started with.

    """

    manifest = get_manifest(ctx)
    console = get_console(ctx)
    entrypoint = entrypoint or manifest.entrypoint

    kwargs = dict(args or [])

    builder = import_builder(builder)

    with console.status("Loading entrypoint module..."):
        try:
            import_module(entrypoint)
        except ModuleNotFoundError as e:
            console.print(f"Could not find entrypoint module {entrypoint}")
            raise e

    app = builder(
        **manifest.to_builder_dict(),
        **builder_kwargs,
    )

    panel = construct_run_panel(app)
    console.print(panel)

    asyncio.run(call_app(console, app, template, kwargs))
