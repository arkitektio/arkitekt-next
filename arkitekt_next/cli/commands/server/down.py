import rich_click as click
from click import Context
from dokker.projects.dokker import DokkerProject
from dokker.loggers.print import PrintLogger
from dokker.deployment import Deployment
from typing import Optional
import os
from .utils import compile_options


@click.command()
@click.option(
    "--name",
    help="The name of the deployment",
    default=None,
    required=False,
    type=click.Choice(compile_options()),
)
@click.pass_context
def down(
    ctx: Context,
    name: Optional[str] = None,
) -> None:
    """
    Down a deployment

    Removing a deployment will stop all containers and call docker compose down
    on the project. This will remove all containers and networks created by the
    deployment. The deployment will still be available in the .dokker folder
    However (depending on your settings) data that was stored in volumes managed
    by the deployment will be removed.

    If you want to simple Stop the deployment, use the stop command instead.

    """
    if not name:
        options = compile_options()
        if not options:
            raise click.ClickException(
                "No deployments found. Please run arkitekt_next server init first"
            )

        name = options[0]

    print(f"Running {name}")

    project = DokkerProject(
        name=name,
    )

    deployment = Deployment(project=project, logger=PrintLogger())
    with deployment:
        deployment.down()
        print("Shutting down...")

    print("Done")
