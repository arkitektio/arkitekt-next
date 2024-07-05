import rich_click as click


import rich_click as click
from .variables import variables
from .templates import templates
from .requirements import requirements


@click.group()
@click.pass_context
def inspect(ctx):
    """Inspects your arkitekt_next app

    Inspects various parts of your arkitekt_next app. This is useful for debugging
    and development. It also represents methods that are called by the arkitekt_next
    server when you run your app in production mode.

    """


inspect.add_command(variables, "variables")
inspect.add_command(requirements, "requirements")
inspect.add_command(templates, "templates")
