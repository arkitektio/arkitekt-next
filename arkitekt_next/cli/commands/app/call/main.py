""" Calling functions in your arkitekt_next app"""

from click import Context
import rich_click as click


from .remote import remote
from arkitekt_next.cli.docs import CALL_DOCS, help_epilog


@click.group(epilog=help_epilog(CALL_DOCS))
@click.pass_context
def call(ctx: Context) -> None:
    """Call functions in your arkitekt_next app.

    Calls always go through a rekuest server: the function is assigned and run
    remotely using rekuest/fakts. Only nodes that are available on the connected
    server can be called.
    """


call.add_command(remote, "remote")
