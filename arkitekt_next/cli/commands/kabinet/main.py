import rich_click as click

from click import Context


class LazyGroup(click.Group):

    def list_commands(self, ctx):
        return ["build", "init", "validate", "publish", "stage", "wizard"]

    def get_command(self, ctx, cmd_name):
        from .build import build
        from .publish import publish
        from .stage import stage
        from .init import init
        from .validate import validate

        if cmd_name == "build":
            return build
        elif cmd_name == "init":
            return init
        elif cmd_name == "validate":
            return validate
        elif cmd_name == "publish":
            return publish
        elif cmd_name == "stage":
            return stage
        return None


@click.group(cls=LazyGroup)
@click.pass_context
def kabinet(ctx: Context) -> None:
    """Deploy the arkitekt_next app with Port

    The port deployer is an arkitekt_next plugin service, which allows you to deploy your arkitekt_next app to
    any arkitekt_next instance and make it instantly available to the world. Port uses docker to containerize
    your application and will publish it locally to your dockerhub account, and mark it locally as
    deployed. People can then use your github repository to deploy your app to their arkitekt_next instance.

    """

    pass
