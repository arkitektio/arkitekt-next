import rich_click as click
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from arkitekt_next.cli.vars import get_console, get_manifest, get_work_dir
from arkitekt_next.cli.constants import compile_scopes
from arkitekt_next.cli.io import write_manifest


@click.group("scopes")
@click.pass_context
def scopes_group(ctx):
    """Inspect, add and remove scopes for this arkitekt-next app."""
    pass


@scopes_group.command("add")
@click.argument("SCOPE", nargs=-1, type=click.Choice(compile_scopes()))
@click.pass_context
def add_scopes(ctx, scope):
    """Add one or more scopes to this app."""
    if not scope:
        raise click.ClickException("Please provide at least one scope")

    manifest = get_manifest(ctx)
    console = get_console(ctx)
    manifest.scopes = list(set(list(scope) + list(manifest.scopes)))
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Scopes updated to {manifest.scopes}")


@scopes_group.command("remove")
@click.argument("SCOPE", nargs=-1, type=click.Choice(compile_scopes()))
@click.pass_context
def remove_scopes(ctx, scope):
    """Remove one or more scopes from this app."""
    if not scope:
        raise click.ClickException("Please provide at least one scope to remove")

    manifest = get_manifest(ctx)
    console = get_console(ctx)
    manifest.scopes = list(set(manifest.scopes) - set(scope))
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Scopes updated to {manifest.scopes}")


@scopes_group.command("list")
@click.pass_context
def list_scopes(ctx):
    """List currently active scopes for this app."""
    manifest = get_manifest(ctx)
    console = get_console(ctx)

    table = Table.grid(padding=(0, 1))
    table.add_column("Scope")
    table.add_column("Description")
    for scope in manifest.scopes:
        table.add_row(scope, "")

    console.print(Panel(
        Group("[bold green]Demanded Scopes[/]", table),
        title_align="center",
        border_style="green",
        style="white",
    ))


@scopes_group.command("available")
@click.pass_context
def list_available(ctx):
    """List all scopes available in the platform."""
    console = get_console(ctx)

    table = Table.grid(padding=(0, 1))
    table.add_column("Scope")
    table.add_column("Description")
    for scope in compile_scopes():
        table.add_row(scope, "")

    console.print(Panel(
        Group("[bold green]Available Scopes[/]", table),
        title_align="center",
        border_style="green",
        style="white",
    ))
