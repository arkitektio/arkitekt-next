import rich_click as click
from arkitekt_next.cli.commands.app.run.dev import resolve_entrypoint
from arkitekt_next.cli.options import (
    with_fakts_next_url,
    with_builder,
    with_token,
    with_redeem_token,
    with_force,
    with_headless,
    with_log_level,
    with_skip_cache,
    with_version,
)
from arkitekt_next.cli.vars import get_console, get_manifest
import asyncio
from arkitekt_next.cli.ui import construct_run_panel
from importlib import import_module
from .utils import import_builder, run_app
import sys


@click.command("prod")
@with_fakts_next_url
@with_builder
@with_token
@with_redeem_token
@with_force
@with_headless
@with_log_level
@with_skip_cache
@with_version
@click.argument("entrypoint", required=False)
@click.pass_context
def prod(ctx, entrypoint=None, builder=None, version=None, **builder_kwargs):
    """Runs the app in production mode

    \n
    You can specify the builder to use with the --builder flag. By default, the easy builder is used, which is designed to be easy to use and to get started with.

    """

    manifest = get_manifest(ctx)
    console = get_console(ctx)
    entrypoint = entrypoint or manifest.entrypoint

    builder = import_builder(builder)

    entrypoint_module, entrypoint_file = resolve_entrypoint(entrypoint)

    with console.status("Loading entrypoint module..."):
        try:
            import_module(entrypoint_module)
        except ModuleNotFoundError as e:
            console.print(f"Could not find entrypoint module {entrypoint_module}")
            raise e

    # Build from the manifest; let --version override the manifest version if given.
    builder_args = {**manifest.to_builder_dict(), **builder_kwargs}
    if version:
        builder_args["version"] = version

    app = builder(**builder_args)

    panel = construct_run_panel(app)
    console.print(panel)

    try:
        asyncio.run(run_app(app))
    except Exception as e:
        console.print_exception()
        sys.exit(1)
