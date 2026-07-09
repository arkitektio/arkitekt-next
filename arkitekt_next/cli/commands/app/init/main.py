import rich_click as click
import os
import shutil
import subprocess
from arkitekt_next.cli.constants import compile_scopes, compile_templates
from arkitekt_next.cli.interactive import require_interactive
from arkitekt_next.cli.utils import build_relative_dir
from getpass import getuser
from arkitekt_next.cli.types import Manifest
from arkitekt_next.cli.vars import get_console, get_work_dir
import semver
from arkitekt_next.cli.io import write_manifest, load_manifest
from arkitekt_next.cli.docs import INIT_DOCS, help_epilog
from rich.panel import Panel
from typing import Optional, List


#: Non-interactive escape hatch surfaced when `app init` needs to prompt.
_INIT_HINT = "Pass --yes to accept the defaults, or provide the fields as options."


def get_default_package_manager():
    if shutil.which("uv"):
        return "uv"
    return "pip"


@click.command(epilog=help_epilog(INIT_DOCS))
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
    parent_work_dir = get_work_dir(ctx)

    # Resolve the target directory without changing process CWD
    if path != ".":
        work_dir = os.path.join(parent_work_dir, path)
        os.makedirs(work_dir, exist_ok=True)
    else:
        work_dir = parent_work_dir

    if not identifier:
        default_identifier = os.path.basename(work_dir)
        if yes:
            identifier = default_identifier
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            identifier = click.prompt("Your app identifier", default=default_identifier)

    if not author:
        if yes:
            author = getuser()
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            author = click.prompt("Your name", default=getuser())

    if not entrypoint:
        if yes:
            entrypoint = "app"
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            entrypoint = click.prompt("Your app file", default="app")

    if not semver.Version.is_valid(version):
        if yes:
            raise click.ClickException(
                f"Invalid version: {version}. ArkitektNext versions need to follow semver."
            )
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            while not semver.Version.is_valid(version):
                get_console(ctx).print(
                    "ArkitektNext versions need to follow [link=https://semver.org]semver[/link]. Please choose a correct format (examples: 0.0.0, 0.1.0, 0.0.0-alpha.1)"
                )
                version = click.prompt(
                    "The version of your app",
                    default="0.0.1",
                )

    existing_manifest = load_manifest(base_dir=work_dir)
    if existing_manifest and not overwrite_manifest:
        if yes:
            should_overwrite = True
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            should_overwrite = click.confirm(
                f"Another ArkitektNext app {existing_manifest.to_console_string()} exists already at {work_dir}?. Do you want to overwrite?",
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

        pyproject = os.path.join(work_dir, "pyproject.toml")
        if not os.path.exists(pyproject):
            subprocess.run(
                ["uv", "init", "--name", identifier, "--no-workspace"],
                check=True,
                cwd=work_dir,
            )
            extras_string = ",".join(with_extra)
            package_spec = (
                f"arkitekt-next[{extras_string}]" if with_extra else "arkitekt-next"
            )
            subprocess.run(["uv", "add", package_spec], check=True, cwd=work_dir)
            hello_py = os.path.join(work_dir, "hello.py")
            if os.path.exists(hello_py) and entrypoint != "hello":
                os.remove(hello_py)
        else:
            console.print(
                "pyproject.toml already exists. Skipping uv init.", style="yellow"
            )

    with open(build_relative_dir("templates", f"{template}.py")) as f:
        template_app = f.read()

    entrypoint_file = os.path.join(work_dir, f"{entrypoint}.py")
    if os.path.exists(entrypoint_file) and not overwrite_app:
        if yes:
            should_overwrite = True
        else:
            require_interactive("`app init`", hint=_INIT_HINT)
            should_overwrite = click.confirm(
                "Entrypoint File already exists. Do you want to overwrite?"
            )
        if should_overwrite:
            with open(entrypoint_file, "w") as f:
                f.write(template_app)
    else:
        with open(entrypoint_file, "w") as f:
            f.write(template_app)

    write_manifest(manifest, base_dir=work_dir)
    md = Panel(
        f"{manifest.to_console_string()} was successfully initialized\n\n"
        + "[not bold white]We are excited to see what you come up with!",
        border_style="green",
        style="green",
    )
    console.print(md)
