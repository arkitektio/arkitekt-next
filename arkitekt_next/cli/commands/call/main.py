""" Calling functions in your arkitekt_next app"""

from click import Context
import rich_click as click


from .remote import remote


@click.group()
@click.pass_context
def call(ctx: Context) -> None:
    """Call functions in your arkitekt_next app.
    
    This command allows you to call functions in your app 
    either locally or remotely.
    
    Locally, you can call functions that are defined in your app
    without needing to use rekuest or fakts. (No Server for assignment needed)
    
    Remotely, you can call functions that are defined in your app
    using rekuest or fakts. This goes through a rekuest server to
    remote call the function.
    
    """


call.add_command(remote, "remote")
