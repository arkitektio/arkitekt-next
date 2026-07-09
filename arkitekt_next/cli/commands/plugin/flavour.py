import rich_click as click
# `flavour add` reuses the plugin `init` scaffolder.
from .init import init

@click.group()
def flavour():
    """
    Manage flavours
    """
    pass

# Register init as add
flavour.add_command(init, name="add")
