from pydantic import BaseModel
import rich_click as click
from importlib import import_module
from arkitekt_next.apps.types import App
from arkitekt_next.cli.commands.run.utils import import_builder
from arkitekt_next.cli.vars import get_console, get_manifest
from arkitekt_next.cli.options import with_builder
import json
import os


async def run_app(app):
    async with app:
        await app.rekuest.run()


@click.command("prod")
@click.pass_context
@click.option(
    "--pretty",
    "-p",
    help="Should we just output json?",
    is_flag=True,
    default=False,
)
@click.option(
    "--machine-readable",
    "-mr",
    help="Should we just output json?",
    is_flag=True,
    default=False,
)
@with_builder
def templates(
    ctx,
    pretty: bool,
    machine_readable: bool,
    builder: str = "arkitekt_next.builders.easy",
):
    """Runs the app in production mode

    \n
    You can specify the builder to use with the --builder flag. By default, the easy builder is used, which is designed to be easy to use and to get started with.

    """

    manifest = get_manifest(ctx)
    console = get_console(ctx)

    entrypoint = manifest.entrypoint
    identifier = manifest.identifier
    entrypoint_file = f"{manifest.entrypoint}.py"
    os.path.realpath(entrypoint_file)

    builder_func = import_builder(builder)

    entrypoint = manifest.entrypoint

    with console.status("Loading entrypoint module..."):
        try:
            import_module(entrypoint)
        except ModuleNotFoundError as e:
            console.print(f"Could not find entrypoint module {entrypoint}")
            raise e

    app: App = builder_func(
        identifier=identifier,
        version="dev",
        logo=manifest.logo,
    )

    rekuest = app.services.get("rekuest")
    if rekuest is None:
        console.print("No rekuest service found in app")
        return
    
    x = {
        key: item.model_dump(by_alias=True)
        for key, item in rekuest.agent.extensions[
            "default"
        ].definition_registry.templates.items()
    }
    if machine_readable:
        print("--START_TEMPLATES--" + json.dumps(x) + "--END_TEMPLATES--")

    else:
        if pretty:
            console.print(json.dumps(x, indent=2))
        else:
            print(json.dumps(x))
