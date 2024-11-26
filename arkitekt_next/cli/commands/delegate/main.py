import rich_click as click


import rich_click as click
from .script import script


@click.group()
@click.pass_context
def delegate(ctx):
    """Inspects your arkitekt_next app

    Inspects various parts of your arkitekt_next app. This is useful for debugging
    and development. It also represents methods that are called by the arkitekt_next
    server when you run your app in production mode.

    """


delegate.add_command(script, "script")
