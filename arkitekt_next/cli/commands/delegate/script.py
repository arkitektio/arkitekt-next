import rich_click as click
from arkitekt_next.cli.options import *
import asyncio
from arkitekt_next.cli.ui import construct_run_panel
from importlib import import_module
from arkitekt_next.cli.utils import import_builder
from rekuest_next.agents.extensions.delegating.extension import CLIExtension
from rekuest_next.api.schema import NodeKind, BindsInput
from rich.table import Table
from rich.console import Console
from typing import Dict, Any

from rekuest_next.rekuest import RekuestNext


async def call_app(
    console: Console,
    app: App,
    template_string: str,
    arg: Dict[str, Any],
):
    async with app:
        await app.services.get("rekuest").agent.aprovide()


@click.command("prod")
@click.argument("script_name", type=str, required=True, nargs=-1)
@click.option(
    "--url",
    help="The fakts_next url for connection",
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
def script(
    ctx,
    script_name,
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

    app = builder(
        **manifest.to_builder_dict(),
        **builder_kwargs,
    )

    rekuest: RekuestNext = app.services.get("rekuest")

    rekuest.agent.register_extension("cli", CLIExtension(" ".join(script_name)))

    panel = construct_run_panel(app)
    console.print(panel)

    asyncio.run(call_app(console, app, template, kwargs))
