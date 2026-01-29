import rich_click as click
from arkitekt_next.cli.commands.kabinet.init import init

@click.group()
def flavour():
    """
    Manage flavours
    """
    pass

# Register init as add
flavour.add_command(init, name="add")
