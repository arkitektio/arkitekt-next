import rich_click as click

from arkitekt_next.cli.docs import COORD_DOCS, help_epilog
from arkitekt_next.cli.vars import get_console
from arkitekt_next.cli.commands._server_common import (
    COORD_CONFIG_FILENAME,
    compose_and_up,
    resolve_path,
    write_profile,
)


@click.group(epilog=help_epilog(COORD_DOCS))
@click.pass_context
def coord(ctx) -> None:
    """Run a coordinator: the standalone Lok auth server + Kontrol frontend.

    A coordinator issues identity (OIDC/JWKS via Lok) and serves the Kontrol web
    frontend that clients and hubs authenticate against. It runs no data/compute
    services and no deployer -- point one or more `hub`s at it via their
    `--coord-server`.
    """


@coord.command()
@click.argument("path", required=False)
@click.option(
    "--template",
    "-t",
    default=None,
    help="Config template (stable, dev, default, minimal). If omitted, the interactive wizard runs and asks whether to set up organizations.",
)
@click.option("--wizard", "-w", is_flag=True, help="Force the interactive configuration wizard.")
@click.option("--default", "-d", "use_default", is_flag=True, help="Accept all defaults (skip the wizard, no prompts).")
@click.option("--port", type=int, default=None, help="Exposed HTTP port.")
@click.option("--ssl-port", type=int, default=None, help="Exposed HTTPS port.")
@click.option("--backend", default="docker", help="Deployment backend (docker, podman, kubernetes).")
@click.pass_context
def init(ctx, path, template, wizard, use_default, port, ssl_port, backend) -> None:
    """Initialize a coordinator configuration (Lok + Kontrol only).

    With no `--template`, the interactive wizard runs and asks whether to set up
    organizations. Passing a `--template` or `--default` skips all questioning
    and uses defaults.
    """
    from arkitekt_next.server.config import CoordConfig
    from arkitekt_next.server.templates import apply_template
    from arkitekt_next.server.wizard import prompt_coord_config

    console = get_console(ctx)
    target = resolve_path(ctx, path)

    # No template chosen -> interactive wizard, unless --default accepts the defaults.
    run_wizard = (wizard or template is None) and not use_default
    config = prompt_coord_config(console) if run_wizard else CoordConfig()

    if port is not None:
        config.gateway.exposed_http_port = port
    if ssl_port is not None:
        config.gateway.exposed_https_port = ssl_port

    if template is not None:
        config = apply_template(config, template)

    console.print(
        f"Creating [bold]coordinator[/bold] ({template or 'wizard'}) with Lok + Kontrol "
        f"at [cyan]{target}[/cyan]..."
    )
    write_profile(
        ctx, target, config, filename=COORD_CONFIG_FILENAME, kind="coord", backend=backend
    )


@coord.command()
@click.argument("path", required=False)
@click.pass_context
def up(ctx, path) -> None:
    """Compose the coordinator (Lok + auth wiring) and run `docker compose up`."""
    from arkitekt_next.server.config import CoordConfig
    from arkitekt_next.server.diff import write_coord_files

    compose_and_up(
        ctx,
        resolve_path(ctx, path),
        filename=COORD_CONFIG_FILENAME,
        model_cls=CoordConfig,
        generator=write_coord_files,
    )
