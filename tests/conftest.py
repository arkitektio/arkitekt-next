from __future__ import annotations
from typing import TYPE_CHECKING, Generator
from dataclasses import dataclass
import shutil
import subprocess
import pytest
from arkitekt_next.cli.main import cli
from click.testing import CliRunner

if TYPE_CHECKING:
    from arkitekt_next.server.dev import ArkitektServer
    from arkitekt_next.app import App


def _docker_available() -> bool:
    """Return True if a docker CLI and a reachable daemon are present."""
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Gate tests that need external services.

    Every test runs by default, except:
    - ``integration`` tests (which require a running arkitekt-server) — skipped
      unless explicitly selected with ``-m integration``;
    - ``needs_docker`` tests — skipped when no docker daemon is reachable, so
      they no-op on macOS/Windows CI runners and dev machines without docker.
    """
    docker_ok = _docker_available()
    # `-m integration` selects integration tests; only then do we run them.
    run_integration = "integration" in str(config.getoption("markexpr") or "")
    skip_no_docker = pytest.mark.skip(reason="docker daemon not available")
    skip_integration = pytest.mark.skip(
        reason="integration tests require a running arkitekt-server; run with -m integration"
    )
    for item in items:
        # Use get_closest_marker (not `in item.keywords`): keywords also contain
        # path-derived names like the `cli` directory, which would over-match.
        if item.get_closest_marker("integration") is not None and not run_integration:
            item.add_marker(skip_integration)
        if item.get_closest_marker("needs_docker") is not None and not docker_ok:
            item.add_marker(skip_no_docker)


@pytest.fixture(autouse=True)
def _assume_interactive(monkeypatch):
    """Make the CLI treat itself as interactive during tests.

    ``CliRunner`` replaces ``sys.stdin`` with a non-TTY stream, so the
    ``require_interactive`` guard (added to every prompt site) would abort any
    test that drives a prompt via ``input=``. Tests that specifically exercise
    the non-TTY guard patch ``is_interactive`` back to ``False`` themselves.
    """
    monkeypatch.setattr(
        "arkitekt_next.cli.interactive.is_interactive", lambda: True
    )



@pytest.fixture
def initialized_app_cli_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "app",
                "init",
                "--identifier",
                "arkitekt-next",
                "--version",
                "0.0.1",
                "--author",
                "arkitek",
                "--template",
                "simple",
                "--scopes",
                "read",
                "--scopes",
                "write",
            ],
        )
        assert result.exit_code == 0, result.output
        yield runner


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def app_dir(tmp_path):
    """Temp dir with an initialized app, using --work-dir (no os.chdir)."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--work-dir",
            str(tmp_path),
            "app",
            "init",
            "--identifier",
            "com.test.app",
            "--version",
            "0.0.1",
            "--author",
            "tester",
            "--entrypoint",
            "app",
            "--package-manager",
            "pip",
        ],
    )
    assert result.exit_code == 0, result.output
    return tmp_path


@pytest.fixture
def app_runner(app_dir):
    """CliRunner paired with a pre-initialized app directory."""
    runner = CliRunner()
    return runner, app_dir


@dataclass
class AppWithinDeployment:
    """Dataclass to hold the running Arkitekt server and the connected app."""
    server: ArkitektServer
    app: App


# Services the upload integration test needs: ``mikro`` provides the image/dataset
# API, ``rekuest`` is part of the default service registry that ``easy`` negotiates
# against. ``lok`` is always enabled (see ``REQUIRED_SERVICES``).
INTEGRATION_SERVICES = ["rekuest", "mikro", "kabinet"]

# lok auto-configures a local hub with this identifier from the default
# kommunity partners that ``arkitekt-server`` writes into the generated config.
# ``validatecode`` resolves the device code against it.
HUB_IDENTIFIER = "localhost"


@pytest.fixture(scope="session")
def lok_server() -> Generator[ArkitektServer, None, None]:
    """Spin up a lok-only Arkitekt deployment (gateway + lok + infra).

    Much faster to boot than the full ``arkitekt_server`` stack; use it for
    CLI integration tests that only talk to the coordination server. Control
    lok through ``lok_server.lok`` (approve device codes, authorize
    hubs, run management commands).
    """
    from arkitekt_next.server.dev import temp_setup

    with temp_setup([], channel="next") as server:
        setup = server.setup
        with setup:
            setup.pull()
            setup.up()
            setup.check_health()
            yield server
            setup.down()


@pytest.fixture(scope="session")
def arkitekt_server() -> Generator[ArkitektServer, None, None]:
    """Spin up an ephemeral Arkitekt server with the services needed for tests.

    Uses ``temp_setup`` which writes a throwaway config (anonymous volumes,
    randomized ports), builds a ``dokker`` testing deployment and pre-registers a
    health check for every enabled web service. The deployment is started here and
    torn down on teardown.
    """
    from arkitekt_next.server.dev import temp_setup

    with temp_setup(INTEGRATION_SERVICES, channel="next") as server:
        setup = server.setup
        with setup:
            setup.pull()
            setup.up()
            setup.check_health()
            yield server
            setup.down()


@pytest.fixture(scope="session")
def running_app(
    arkitekt_server: ArkitektServer,
) -> Generator[AppWithinDeployment, None, None]:
    """Connect an ``easy`` app to the running Arkitekt server.

    The device-code login is auto-approved through the lok controller (which
    runs lok's ``validatecode`` management command inside the container).
    """
    from fakts_next.grants.remote import FaktsEndpoint
    from arkitekt_next import easy
    from arkitekt_next.service_registry import get_default_service_registry

    async def device_code_hook(endpoint: FaktsEndpoint, device_code: str):
        await arkitekt_server.lok.avalidate_device_code(
            device_code, hub=HUB_IDENTIFIER
        )

    registry = get_default_service_registry()
    assert registry, "Service registry must be initialized"

    with easy(
        url=arkitekt_server.gateway_url,
        device_code_hook=device_code_hook,
    ) as app:
        yield AppWithinDeployment(server=arkitekt_server, app=app)
