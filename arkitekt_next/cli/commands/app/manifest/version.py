import rich_click as click
from semver import Version
from arkitekt_next.cli.vars import get_console, get_manifest, get_work_dir
from arkitekt_next.cli.io import write_manifest


@click.group()
@click.pass_context
def version(ctx):
    """Updates the version of the arkitekt_next app

    ArkitektNext manifests versioning follow [link=https://semver.org]semver[/link] and are used to version the app.
    This provides an orthogonal way to version the app, beyond node versioning. The version is used to
    track changes and to provide a way to update the app in the platform. For more information, please visit
    [link=https://arkitekt.live]https://arkitekt.live[/link]

    """


@version.command("set")
@click.argument("VERSION", type=str, required=False)
@click.pass_context
def set_version(ctx, version):
    """Sets the version of the arkitekt_next app

    When setting the version, you can either provide a version, or you can let the cli
    prompt you for a version. If you provide a version, it will be parsed and validated
    against semver. If you let the cli prompt you, it will try to parse the current version
    and suggest a new version based on that. If the current version is not a valid semver
    version, it will prompt you for a new version without a suggestion.
    """

    manifest = get_manifest(ctx)
    console = get_console(ctx)
    work_dir = get_work_dir(ctx)
    old_version = manifest.version

    if not version:
        try:
            potential_new_version = str(Version.parse(old_version).bump_patch())
        except Exception:
            potential_new_version = None

        new_version = click.prompt(
            "Please provide a new version", default=potential_new_version, type=str
        )
        Version.parse(new_version)
        version = new_version

    manifest.version = version
    write_manifest(manifest, base_dir=work_dir)
    console.print(f"Version Updated from {old_version} to {version}")


@version.command()
@click.pass_context
def patch(ctx):
    """ "Patches the version of the arkitekt_next app


    Patches the version of the arkitekt_next app, by bumping the patch number.
    E.g. from 1.0.1 to 1.0.2. This should be used for bugfixes and small changes.
    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    old_version = manifest.version
    manifest.version = str(Version.parse(old_version).bump_patch())
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Version Updated from {old_version} to {manifest.version}")


@version.command()
@click.pass_context
def minor(ctx):
    """Bumps the minor version number of the arkitekt_next app

    Patches the version of the arkitekt_next app, by bumping the minor number.
    E.g. from 1.0.1 to 1.1.1. This should be used for new features, that
    are backwards compatible.

    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    old_version = manifest.version
    manifest.version = str(Version.parse(old_version).bump_minor())
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Version Updated from {old_version} to {manifest.version}")


@version.command()
@click.pass_context
def major(ctx):
    """Increase the major version of the arkitekt_next app"

    Patches the version of the arkitekt_next app, by bumping the major number.
    E.g. from 1.0.1 to 2.0.1, This should be used for breaking changes,
    that are not backwards compatible (e.g. deleting a node).

    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    old_version = manifest.version
    manifest.version = str(Version.parse(old_version).bump_major())
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Version Updated from {old_version} to {manifest.version}")


@version.command()
@click.pass_context
def prerelease(ctx):
    """Patches the prerelease of the arkitekt_next app"


    Patches the version of the arkitekt_next app, by bumping the prerelease number.
    E.g. from 1.0.1 to 1.0.1-alpha.1
    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    old_version = manifest.version
    manifest.version = str(Version.parse(old_version).bump_prerelease())
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Version Updated from {old_version} to {manifest.version}")


@version.command("build")
@click.pass_context
def build_version(ctx):
    """Patches the build of the arkitekt_next app

    Patches the version of the arkitekt_next app, by bumping the build number.
    E.g. from 1.0.1 to 1.0.1+1, This should be used for changes that are not
    reflected in the version number, but are still important to track (e.g. a
    hotfix).

    """
    manifest = get_manifest(ctx)
    console = get_console(ctx)
    old_version = manifest.version
    manifest.version = str(Version.parse(old_version).bump_build())
    write_manifest(manifest, base_dir=get_work_dir(ctx))
    console.print(f"Version Updated from {old_version} to {manifest.version}")
