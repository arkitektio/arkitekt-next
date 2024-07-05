import rich_click as click
from .build import build
from .publish import publish
from .stage import stage
from .init import init
from .wizard import wizard
from .validate import validate
from click import Context


@click.group()
@click.pass_context
def kabinet(ctx: Context) -> None:
    """Deploy the arkitekt_next app with Port

    The port deployer is an arkitekt_next plugin service, which allows you to deploy your arkitekt_next app to
    any arkitekt_next instance and make it instantly available to the world. Port uses docker to containerize
    your application and will publish it locally to your dockerhub account, and mark it locally as
    deployed. People can then use your github repository to deploy your app to their arkitekt_next instance.

    """

    pass


kabinet.add_command(build, "build")
kabinet.add_command(init, "init")
kabinet.add_command(validate, "validate")
kabinet.add_command(publish, "publish")
kabinet.add_command(stage, "stage")
kabinet.add_command(wizard, "wizard")
