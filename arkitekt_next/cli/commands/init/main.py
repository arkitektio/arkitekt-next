import rich_click as click
import os
import shutil
import subprocess
from arkitekt_next.cli.constants import *
from getpass import getuser
from arkitekt_next.cli.types import Manifest, Requirement
from arkitekt_next.cli.vars import get_manifest, get_console
import semver
from arkitekt_next.cli.io import write_manifest, load_manifest
from rich.panel import Panel
from typing import Optional, List


def ensure_semver(ctx, param, value):
    """Callback to check and prompt for file overwrite."""

    if not value:
        value = click.prompt(
            "The version of your app",
            default="0.0.1",
        )

    while not semver.Version.is_valid(value):
        get_console(ctx).print(
            "ArkitektNext versions need to follow [link=https://semver.org]semver[/link]. Please choose a correct format (examples: 0.0.0, 0.1.0, 0.0.0-alpha.1)"
        )
        value = click.prompt(
            "The version of your app",
            default="0.0.1",
        )

    return value


def get_default_package_manager():
    if shutil.which("uv"):
        return "uv"
    return "pip"


@click.command()
@click.argument("path", type=click.Path(), default=".", required=False)
@click.option(
    "--overwrite-manifest",
    "-om",
    help="Should we overwrite the existing manifest if it already exists?",
    is_flag=True,
    default=False,
)
@click.option(
    "--template",
    "-t",
    help="The template to use. You can choose from a variety of preconfigured templates. They are just starting points and can be changed later.",
    type=click.Choice(compile_templates()),
    default="simple",
)
@click.option(
    "--identifier",
    "-i",
    help="The identifier of your app. This will be used to identify your app in the ArkitektNext ecosystem. It should be unique and should follow the [link=https://en.wikipedia.org/wiki/Reverse_domain_name_notation]reverse domain name notation[/link] (example: com.example.myapp)",
    required=False,
)
@click.option(
    "--version",
    "-v",
    help="The version of your app. Needs to follow [link=https://semver.org/]semantic versioning[/link].",
    default="0.0.1",
)
@click.option(
    "--author",
    help="The author of your app. This will be shown to users of your app",
    required=False,
    default=None,
)
@click.option(
    "--logo",
    help="Which logo to use for this app, needs to be a valid url",
    required=False,
)
@click.option(
    "--entrypoint",
    "-e",
    help="The entrypoint of your app. This will be the name of the python file. Omit the .py ending",
    required=False,
    default=None,
)
@click.option(
    "--overwrite-app",
    "-oa",
    help="Do you want to overwrite the app file if it exists?",
    is_flag=True,
    default=False,
)
@click.option(
    "--scopes",
    "-s",
    help="The scopes of the app. You can choose multiple for your app. For a list of scopes, run `arkitekt_next manifest scopes available`",
    type=click.Choice(compile_scopes()),
    multiple=True,
    default=["read"],
)
@click.option(
    "--package-manager",
    "-pm",
    help="The package manager to use. If uv is selected, it will initialize a project with uv.",
    type=click.Choice(["pip", "uv"]),
    default=get_default_package_manager,
)
@click.option(
    "--yes",
    "-y",
    help="Automatically accept defaults",
    is_flag=True,
    default=False,
)
@click.option(
    "--with-extra",
    help="The extras to install with arkitekt-next. Defaults to all.",
    multiple=True,
    default=["all"],
)
@click.pass_context
def init(
    ctx,
    path: str,
    identifier: str,
    version: str,
    author: str,
    logo: Optional[str],
    scopes: List[str],
    template: str,
    entrypoint: str,
    overwrite_manifest: bool,
    overwrite_app: bool,
    package_manager: str,
    yes: bool,
    with_extra: List[str],
):
    """Initializes an ArkitektNext app

    This command will create a new ArkitektNext app in the current directory. It will
    create a `.arkitekt_next` folder that will contain a manifest and a `app.py` file,
    which will serve as the entrypoint for your app. By default, the app will be
    initialized with a simple hello world app, but you can choose from a variety
    of templates.

    """

    console = get_console(ctx)

    if path != ".":
        os.makedirs(path, exist_ok=True)
        os.chdir(path)

    if not identifier:
        default_identifier = os.path.basename(os.getcwd())
        if yes:
            identifier = default_identifier
        else:
            identifier = click.prompt("Your app identifier", default=default_identifier)

    if not author:
        if yes:
            author = getuser()
        else:
            author = click.prompt("Your name", default=getuser())

    if not entrypoint:
        if yes:
            entrypoint = "app"
        else:
            entrypoint = click.prompt("Your app file", default="app")

    if not semver.Version.is_valid(version):
        if yes:
            # If yes is provided but version is invalid, we should probably fail or fallback to default if it was user provided?
            # But here version has a default "0.0.1" in click option.
            # If user provided an invalid version via flag, we should error.
            # If user didn't provide version, it is "0.0.1" which is valid.
            # So if we are here, user provided invalid version.
            raise click.ClickException(
                f"Invalid version: {version}. ArkitektNext versions need to follow semver."
            )
        else:
            while not semver.Version.is_valid(version):
                get_console(ctx).print(
                    "ArkitektNext versions need to follow [link=https://semver.org]semver[/link]. Please choose a correct format (examples: 0.0.0, 0.1.0, 0.0.0-alpha.1)"
                )
                version = click.prompt(
                    "The version of your app",
                    default="0.0.1",
                )

    manifest = load_manifest()
    if manifest and not overwrite_manifest:
        if yes:
            should_overwrite = True
        else:
            should_overwrite = click.confirm(
                f"Another ArkitektNext app {manifest.to_console_string()} exists already at {os.getcwd()}?. Do you want to overwrite?",
                abort=True,
            )
        if not should_overwrite:
            ctx.abort()

    manifest = Manifest(
        logo=logo,
        author=author,
        identifier=identifier,
        version=version,
        scopes=scopes,
        entrypoint=entrypoint,
        package_manager=package_manager,
    )

    if package_manager == "uv":
        if not shutil.which("uv"):
            raise click.ClickException(
                "uv is not installed. Please install uv or choose another package manager."
            )

        if not os.path.exists("pyproject.toml"):
            subprocess.run(
                ["uv", "init", "--name", identifier, "--no-workspace"],
                check=True,
                cwd=os.getcwd(),
            )
            extras_string = ",".join(with_extra)
            package_spec = (
                f"arkitekt-next[{extras_string}]" if with_extra else "arkitekt-next"
            )

            subprocess.run(["uv", "add", package_spec], check=True, cwd=os.getcwd())
            if os.path.exists("hello.py") and entrypoint != "hello":
                os.remove("hello.py")
        else:
            console.print(
                "pyproject.toml already exists. Skipping uv init.", style="yellow"
            )

    with open(build_relative_dir("templates", f"{template}.py")) as f:
        template_app = f.read()

    if os.path.exists(f"{entrypoint}.py") and not overwrite_app:
        if yes:
            should_overwrite = True
        else:
            should_overwrite = click.confirm(
                "Entrypoint File already exists. Do you want to overwrite?"
            )
        if should_overwrite:
            with open(f"{entrypoint}.py", "w") as f:
                f.write(template_app)
    else:
        with open(f"{entrypoint}.py", "w") as f:
            f.write(template_app)

    write_manifest(manifest)
    md = Panel(
        f"{manifest.to_console_string()} was successfully initialized\n\n"
        + "[not bold white]We are excited to see what you come up with!",
        border_style="green",
        style="green",
    )
    console.print(md)
