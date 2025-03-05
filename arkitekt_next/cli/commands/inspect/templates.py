import asyncio
from pydantic import BaseModel
import rich_click as click
from importlib import import_module
from arkitekt_next.apps.types import App
from arkitekt_next.cli.commands.run.utils import import_builder
from arkitekt_next.cli.vars import get_console, get_manifest
from arkitekt_next.cli.options import with_builder
import json
import os

from arkitekt_next.constants import DEFAULT_ARKITEKT_URL

from rekuest_next.agents.registry import get_default_extension_registry



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
def templates(
    ctx,
    pretty: bool,
    machine_readable: bool,
    builder: str = "arkitekt_next.builders.easy",
    url: str = DEFAULT_ARKITEKT_URL,
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
        url=url,
        headless=True,
    )

    rekuest = app.services.get("rekuest")
    
    registry =  get_default_extension_registry()
    
    global_list = []
    
    for extension in registry.agent_extensions.values():
        
        definition_registry = extension.get_definition_registry()
        
        to_be_created_templates = tuple(
            x.model_dump() for x in definition_registry.templates.values()
        )
        global_list.extend(to_be_created_templates)
    
    
    
    

    console.print(f"Templates to be created: {len(global_list)}")

    if rekuest is None:
        console.print("No rekuest service found in app")
        return

    if machine_readable:
        print("--START_TEMPLATES--" + json.dumps(global_list) + "--END_TEMPLATES--")

    else:
        if pretty:
            console.print(json.dumps(global_list, indent=2))
        else:
            print(json.dumps(global_list))
