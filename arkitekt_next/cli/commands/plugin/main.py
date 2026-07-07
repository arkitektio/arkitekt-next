import rich_click as click
from click import Context

from arkitekt_next.cli.docs import PLUGIN_DOCS, help_epilog
from arkitekt_next.cli.vars import get_work_dir, set_manifest
from arkitekt_next.cli.io import load_manifest
from arkitekt_next.utils import create_arkitekt_next_folder


class LazyGroup(click.Group):
    """Group that defers importing the (heavy) plugin subcommands until used."""

    def list_commands(self, ctx: Context) -> list[str]:
        return ["init", "build", "validate", "publish", "stage", "flavour", "selector"]

    def get_command(self, ctx: Context, cmd_name: str):
        from .init import init
        from .build import build
        from .publish import publish
        from .stage import stage
        from .validate import validate
        from .flavour import flavour
        from .selector import selector

        return {
            "init": init,
            "build": build,
            "validate": validate,
            "publish": publish,
            "stage": stage,
            "flavour": flavour,
            "selector": selector,
        }.get(cmd_name)


@click.group(cls=LazyGroup, epilog=help_epilog(PLUGIN_DOCS))
@click.pass_context
def plugin(ctx: Context) -> None:
    """Turn your app into a deployable Arkitekt plugin.

    A plugin is an app packaged (via a flavour Dockerfile) so it can be built and
    deployed onto any Arkitekt instance: initialize a flavour (`init`), build and
    publish the image (`build`, `publish`), validate flavours (`validate`), and
    manage flavours/selectors. These commands operate on the app in the current
    working directory and therefore require an already-initialized app — run
    `arkitekt-next app init` first.
    """
    # Guard: plugin commands only make sense inside an initialized app directory.
    # Top-level groups don't get the `app` group's manifest bootstrap, so load it
    # here (and fail clearly if this isn't an app) for the subcommands to use.
    work_dir = get_work_dir(ctx)
    manifest = load_manifest(base_dir=work_dir)
    if manifest is None:
        raise click.ClickException(
            f"No Arkitekt app found in '{work_dir}'. Plugin commands can only be run "
            "inside an initialized app directory — run `arkitekt-next app init` first."
        )

    create_arkitekt_next_folder(base_dir=work_dir)
    set_manifest(ctx, manifest)
