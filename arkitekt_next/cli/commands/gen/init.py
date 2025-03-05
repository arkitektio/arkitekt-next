from importlib import import_module
import os
import shutil
from click import ClickException
import rich_click as click
from arkitekt_next.cli.options import (
    with_documents,
    with_graphql_config,
    with_api_path,
    with_boring,
    with_choose_services,
    with_schemas,
    with_seperate_document_dirs,
)
import yaml
from arkitekt_next.cli.utils import build_relative_dir
from arkitekt_next.cli.vars import get_console, get_manifest
from arkitekt_next.service_registry import get_default_service_registry


@click.command()
@with_seperate_document_dirs
@with_boring
@with_choose_services
@with_graphql_config
@with_api_path
@with_schemas
@with_graphql_config
@with_documents
@click.pass_context
def init(ctx, boring, services, config, documents, schemas, path, seperate_doc_dirs):
    """Initialize code generation for the arkitekt_next app

    Code generation for API's is done with the help of GraphQL Code Generation
    that is powered by turms. This command initializes the code generation for
    the app. It creates the necessary folders and files for the code generation
    to work. It also creates a graphql config file that is used by turms to
    generate the code.

    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    
    entrypoint = manifest.entrypoint

    with console.status("Loading entrypoint module..."):
        try:
            import_module(entrypoint)
        except ModuleNotFoundError as e:
            console.print(f"Could not find entrypoint module {entrypoint}")
            raise e

    
    
    app_directory = os.getcwd()

    app_api_path = os.path.join(app_directory, path)
    app_documents = os.path.join(app_directory, "documents")

    app_schemas = os.path.join(app_directory, "schemas")

    os.makedirs(app_documents, exist_ok=True)
    os.makedirs(app_schemas, exist_ok=True)
    os.makedirs(app_api_path, exist_ok=True)

    # Initializing the config
    projects = {}

    registry = get_default_service_registry()

    chosen_services = registry.service_builders

    if services:
        chosen_services = {
            key: service
            for key, service in registry.service_builders.items()
            if key in services
        }
    else:
        service = click.prompt(
            "Choose a service to initialize the project for",
            type=click.Choice(list(chosen_services.keys())),
        )

        chosen_services = {service: chosen_services[service]}

    if os.path.exists(config):
        if click.confirm(
            f"GraphQL Config file already exists. Do you want to merge your choices?"
        ):
            file = yaml.load(open(config, "r"), Loader=yaml.FullLoader)
            projects = file.get("projects", {})
            click.echo(
                f"Merging {','.join(chosen_services.keys())} in {','.join(projects.keys())}..."
            )

    has_done_something = False

    for key, service in chosen_services.items():
        try:

            schema, project = service.get_graphql_schema(), service.get_turms_project()

            if not schema or not project:
                get_console(ctx).print(f"[red]No schema or project found for {key} [/]")
                continue

            if key in projects:
                get_console(ctx).print(f"[red]Project {key} already exists [/]")
                if not click.confirm("Do you want to overwrite it?"):
                    continue

            has_done_something = True

            if documents:
                os.makedirs(os.path.join(app_documents, key), exist_ok=True)
                if seperate_doc_dirs:
                    os.makedirs(
                        os.path.join(app_documents, key, "queries"), exist_ok=True
                    )
                    os.makedirs(
                        os.path.join(app_documents, key, "mutations"), exist_ok=True
                    )
                    os.makedirs(
                        os.path.join(app_documents, key, "subscriptions"), exist_ok=True
                    )

            if schemas:
                out_path = os.path.join(app_schemas, key + ".schema.graphql")
                with open(out_path, "w") as f:
                    f.write(schema)

            if schemas:
                project["schema"] = os.path.join(app_schemas, key + ".schema.graphql")
            if documents:
                project["documents"] = (
                    os.path.join(app_documents, key) + "/**/*.graphql"
                )

            project["extensions"]["turms"]["out_dir"] = path
            project["extensions"]["turms"]["generated_name"] = f"{key}.py"
            del project["extensions"]["turms"]["documents"]
            del project["schema_url"]

            projects[key] = project

        except Exception as e:
            raise ClickException(
                f"Failed to initialize project for {key}. Error: {e}"
            ) from e

    if has_done_something:
        graph_config_path = os.path.join(app_directory, config)
        yaml.safe_dump(
            {"projects": projects}, open(graph_config_path, "w"), sort_keys=False
        )
        get_console(ctx).print(f"Config file written to {graph_config_path}")
    else:
        get_console(ctx).print("No projects initialized")
        get_console(ctx).print("Exiting...")
