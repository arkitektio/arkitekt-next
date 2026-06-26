from __future__ import annotations
from typing import TYPE_CHECKING, Generator
from dataclasses import dataclass
import shutil
import subprocess
import pytest
from arkitekt_next.cli.main import cli
from click.testing import CliRunner

if TYPE_CHECKING:
    from dokker import Deployment
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
    - ``needs_docker`` tests — skipped when no docker daemon is reachable.
    """
    docker_ok = _docker_available()
    # `-m integration` selects integration tests; only then do we run them.
    run_integration = "integration" in (config.getoption("markexpr") or "")
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


@pytest.fixture
def initialized_app_cli_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
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
    """Dataclass to hold the Arkitekt server deployment."""
    deployment: Deployment
    app: App


@pytest.fixture(scope="session")
def arkitekt_server() -> Generator[Deployment, None, None]:
    """Generates a local Arkitekt server deployment for testing purposes."""
    #TODO CURRENTLY BROKEN, NEEDS TO BE FIXED
    from arkitekt_server.dev import temp_server, ArkitektServerConfig
    from dokker import local

    config = ArkitektServerConfig()

    with temp_server(config) as temp_path:

        setup = local(temp_path / "docker-compose.yaml")

        setup.add_health_check(
            url=lambda spec: f"http://localhost:{spec.find_service('gateway').get_port_for_internal(80).published}/lok/ht",
            service="lok",
            timeout=5,
            max_retries=20,
        )
        with setup as setup:

            setup.pull()
            setup.down()

            setup.up()

            setup.check_health()
            yield setup
            setup.down()


@pytest.fixture(scope="session")
def running_app(arkitekt_server: Deployment) -> Generator[AppWithinDeployment, None, None]:
    """Fixture to ensure the Arkitekt server is running."""
    from fakts_next.grants.remote import FaktsEndpoint
    from arkitekt_next import easy
    from arkitekt_next.service_registry import get_default_service_registry

    async def device_code_hook(endpoint: FaktsEndpoint, device_code: str):
        await arkitekt_server.arun(
            "lok", f"uv run python manage.py validatecode --code {device_code} --user demo --org arkitektio --composition "
        )

    registry = get_default_service_registry()

    assert registry, "Service registry must be initialized"

    with easy(url=f"http://localhost:{arkitekt_server.spec.find_service('gateway').get_port_for_internal(80).published}", device_code_hook=device_code_hook) as app:

        yield AppWithinDeployment(
            deployment=arkitekt_server,
            app=app
        )
