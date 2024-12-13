import rich_click as click
from arkitekt_next.cli.vars import get_manifest
import subprocess
from click import Context
from .io import get_builds
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL


@click.command()
@click.option("--build", help="The build to use", type=str, default=None)
@click.option("--flavour", "-f", help="The flavour to use", default="vanilla")
@click.option(
    "--url",
    "-u",
    help="The fakts_next server to use",
    type=str,
    default=DEFAULT_ARKITEKT_URL,
)
@click.option(
    "--builder",
    help="The builder to use",
    type=str,
    default="arkitekt_next.builders.easy",
)
@click.pass_context
def stage(ctx: Context, build: str, url: str, flavour: str, builder: str) -> None:
    """Stages the latest Build for testing

    Stages the current build for testing. This will create a temporary staged version
    of the app that is run agains the local arkitekt_next instance. The builder will be changed
    to the easy or provided builder to ensure that the app can be run headlessly


    """

    get_manifest(ctx)

    builds = get_builds(build)

    if len(builds) == 0:
        raise click.ClickException("Could not find any builds")

    if len(builds) > 1:
        try:
            build_model = next(
                build for build in builds.values() if build.flavour == flavour
            )
        except StopIteration:
            raise click.ClickException(
                f"Could not find a build for flavour {flavour}. Please run `arkitekt_next port build` "
                + "first to build the flavour"
            )

    else:
        build_model = list(builds.values())[0]

    command = (
        build_model.build_docker_command()
        + build_model.build_arkitekt_next_command(url)
    )

    click.echo(f"Staging build {build} with flavour {flavour} against {url}")
    click.echo("Running command: " + " ".join(command))

    subprocess.run(" ".join(command), shell=True)

    raise click.ClickException("Docker container exited")
