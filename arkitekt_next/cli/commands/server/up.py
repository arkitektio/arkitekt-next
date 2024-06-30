import rich_click as click
from click import Context
from dokker.projects.dokker import DokkerProject
from dokker.loggers.print import PrintLogger
from dokker.deployment import Deployment
from typing import Optional
import os
from .utils import compile_options
from rich.table import Table
from rich.live import Live
from arkitekt_next.cli.vars import get_console


DEFAULT_REPO_URL = (
    "https://raw.githubusercontent.com/jhnnsrs/konstruktor/master/repo/channels.json"
)


@click.command()
@click.option(
    "--name",
    help="The name of the deployment",
    default=None,
    required=False,
    type=click.Choice(compile_options()),
)
@click.pass_context
def up(
    ctx: Context,
    name: Optional[str] = None,
) -> None:
    """
    Ups a deployment

    Up starts your deployment. This will create all containers and networks
    needed for your deployment. If you have not run arkitekt_next server init
    before, this will fail.


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

    console = get_console(ctx)

    logger = PrintLogger(print_function=lambda x: console.log(x))

    deployment = Deployment(project=project, logger=logger)

    with deployment:
        port = deployment.inspect().find_service("lok").get_label("arkitekt_next.link")

        status = console.status(
            f"[bold green]Running on the Lok Server Port {port} Press Ctrl+c once to cancel..."
        )

        with status:
            x = deployment.up(detach=False)
