from arkitekt_next import get_current_service_registry
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
def requirements(
    ctx,
    pretty: bool,
    machine_readable: bool,
):
    """Checks the requirements of the app

    \n
    """

    manifest = get_manifest(ctx)
    console = get_console(ctx)

    entrypoint = manifest.entrypoint
    identifier = manifest.identifier
    entrypoint_file = f"{manifest.entrypoint}.py"
    os.path.realpath(entrypoint_file)


    entrypoint = manifest.entrypoint

    with console.status("Loading entrypoint module..."):
        try:
            import_module(entrypoint)
        except ModuleNotFoundError as e:
            console.print(f"Could not find entrypoint module {entrypoint}")
            raise e


    service_registry = get_current_service_registry()
    
    

    x = [item.model_dump(by_alias=True) for item in service_registry.get_requirements()]
    

    if machine_readable:
        print("--START_REQUIREMENTS--" + json.dumps(x) + "--END_REQUIREMENTS--")

    else:
        if pretty:
            console.print(json.dumps(x, indent=2))
        else:
            print(json.dumps(x))
