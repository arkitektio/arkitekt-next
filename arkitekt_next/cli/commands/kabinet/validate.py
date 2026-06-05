import rich_click as click
from click import Context
from arkitekt_next.cli.vars import get_console, get_work_dir
from .io import get_flavours


@click.command()
@click.option("--flavour", "-f", help="Validate only this flavour.", default=None)
@click.pass_context
def validate(ctx: Context, flavour: str) -> None:
    """Validates all Dockerfiles and flavour configs for this app."""
    console = get_console(ctx)
    work_dir = get_work_dir(ctx)

    flavours = get_flavours(base_dir=work_dir, select=flavour)

    for name in flavours:
        console.print(f"[green]✓[/green] Flavour [bold]{name}[/bold] is valid")

    click.echo("All flavours are valid")
