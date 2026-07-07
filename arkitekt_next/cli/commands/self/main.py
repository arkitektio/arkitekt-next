import rich_click as click
from arkitekt_next.cli.docs import SELF_DOCS, help_epilog
from .upgrade import upgrade
from .version import version
from .info import info


@click.group(epilog=help_epilog(SELF_DOCS))
@click.pass_context
def self_group(ctx) -> None:
    """Manage the Arkitekt CLI / SDK installation itself.

    Meta commands that act on your local Arkitekt installation rather than on a
    specific app: upgrade the installed SDK packages (`upgrade`), print the
    installed version (`version`), or dump environment diagnostics (`info`).
    """


self_group.add_command(upgrade, "upgrade")
self_group.add_command(version, "version")
self_group.add_command(info, "info")
