import rich_click as click
from arkitekt_next.cli.options import *
import asyncio
from arkitekt_next.cli.ui import construct_run_panel
from importlib import import_module
import rich_click as click
from arkitekt_next.cli.options import *
import asyncio
from arkitekt_next.cli.ui import construct_run_panel
from importlib import import_module
from arkitekt_next.cli.utils import import_builder
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL


async def call_app(
    app: App,
    hash,
    arg,
):
    async with app:
        raise NotImplementedError("This is not implemented yet")


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
    "--hash",
    "-h",
    help="The hash of the node to run",
    type=str,
)
def remote(ctx, entrypoint=None, builder=None, args=None, hash=str, **builder_kwargs):
    """ALlows you to run a get the output of a node in a remote app.

    This is useful for debugging and testing. In this mode the app itself will not
    be run, so local nodes cannot be called. Only nodes that are availabble on your
    arkitekt_next server can be called.

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

    asyncio.run(call_app(app, hash, kwargs))
