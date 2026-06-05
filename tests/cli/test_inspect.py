"""Tests for `arkitekt-next inspect` and `kabinet validate`.

These exercise commands that introspect an initialized app. They use the
`app_dir` fixture (a directory with a freshly initialized app, driven via
`--work-dir`).
"""

import sys

import pytest
from click.testing import CliRunner
from arkitekt_next.cli.main import cli


def _invoke(work_dir, *args, **kwargs):
    runner = CliRunner()
    result = runner.invoke(cli, ["--work-dir", str(work_dir), *args], **kwargs)
    if result.exit_code != 0:
        print(result.output)
        print(result.exception)
    return result


# ---------------------------------------------------------------------------
# inspect variables
# ---------------------------------------------------------------------------

def test_inspect_variables_clean_app(app_dir):
    """The default `simple` template has no leaking globals."""
    # `inspect variables` imports the entrypoint module by name ("app"). Python
    # caches imported modules in sys.modules, so drop any cached copy from a
    # previous test to make sure we inspect *this* app_dir's entrypoint.
    sys.modules.pop("app", None)

    result = _invoke(app_dir, "inspect", "variables")
    assert result.exit_code == 0
    assert "No dangerous variables found" in result.output


def test_inspect_variables_detects_leaking_global(app_dir):
    """A module-level mutable variable is reported as dangerous."""
    # Overwrite the entrypoint with a deliberately leaking global.
    (app_dir / "app.py").write_text("leaking_state = []\n")
    sys.modules.pop("app", None)

    result = _invoke(app_dir, "inspect", "variables")
    assert result.exit_code == 0
    assert "leaking_state" in result.output


# ---------------------------------------------------------------------------
# kabinet validate
# ---------------------------------------------------------------------------

def test_kabinet_validate(app_dir):
    """After scaffolding a flavour, validate reports it as valid."""
    init_result = _invoke(
        app_dir,
        "kabinet", "init",
        "--flavour", "vanilla",
        "--arkitekt-version", "0.0.1",
        input="n\n",  # decline the devcontainer prompt
    )
    assert init_result.exit_code == 0

    result = _invoke(app_dir, "kabinet", "validate")
    assert result.exit_code == 0
    assert "vanilla" in result.output
    assert "All flavours are valid" in result.output


def test_kabinet_validate_without_flavours_errors(app_dir):
    """validate fails cleanly when no flavours folder exists yet."""
    result = _invoke(app_dir, "kabinet", "validate")
    assert result.exit_code != 0
    assert "kabinet init" in result.output


# ---------------------------------------------------------------------------
# --help smoke tests — every command group exposes its help text
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "args",
    [
        [],
        ["init"],
        ["run"],
        ["gen"],
        ["kabinet"],
        ["manifest"],
        ["manifest", "version"],
        ["manifest", "scopes"],
        ["inspect"],
        ["call"],
    ],
)
def test_help_for_command_groups(args):
    runner = CliRunner()
    result = runner.invoke(cli, [*args, "--help"])
    assert result.exit_code == 0, result.output
    assert "Usage" in result.output or "Options" in result.output
