import rich_click as click

from arkitekt_next.cli.docs import APP_DOCS, help_epilog
from arkitekt_next.cli.vars import set_manifest, get_work_dir
from arkitekt_next.cli.io import load_manifest
from arkitekt_next.utils import create_arkitekt_next_folder

from arkitekt_next.cli.commands.app.run.main import run
from arkitekt_next.cli.commands.app.gen.main import gen
from arkitekt_next.cli.commands.app.init.main import init
from arkitekt_next.cli.commands.app.manifest.main import manifest
from arkitekt_next.cli.commands.app.inspect.main import inspect
from arkitekt_next.cli.commands.app.call.main import call


@click.group(epilog=help_epilog(APP_DOCS))
@click.pass_context
def app(ctx) -> None:
    """Build, run and deploy ArkitektNext apps from your Python code.

    These are the client-side SDK commands: scaffold a new app (`init`), run it
    locally (`run`), generate typed clients (`gen`), manage its manifest and
    call functions. Every command here operates on the app in the current
    working directory (see `--work-dir`). To package the app as a deployable
    plugin, see the top-level `plugin` group.
    """
    # The app commands operate on a scaffolded project (a manifest inside the
    # `.arkitekt_next` folder). Every subcommand except `init` (which creates that
    # project) needs the folder to exist and the manifest loaded into context.
    # This mirrors the behaviour the root group used to have before the CLI was
    # reorganised into command groups.
    if ctx.invoked_subcommand != "init":
        work_dir = get_work_dir(ctx)
        create_arkitekt_next_folder(base_dir=work_dir)

        manifest = load_manifest(base_dir=work_dir)
        if manifest:
            set_manifest(ctx, manifest)


app.add_command(init, "init")
app.add_command(run, "run")
app.add_command(gen, "gen")
app.add_command(manifest, "manifest")
app.add_command(inspect, "inspect")
app.add_command(call, "call")
