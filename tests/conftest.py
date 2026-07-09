from __future__ import annotations
from typing import TYPE_CHECKING, Generator
from dataclasses import dataclass
import shutil
import subprocess
import pytest
from arkitekt_next.cli.main import cli
from click.testing import CliRunner

if TYPE_CHECKING:
    from arkitekt_server.dev import ArkitektServer
    from arkitekt_next.app import App





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
    """Dataclass to hold the running Arkitekt server and the connected app."""
    server: ArkitektServer
    app: App


# Services the upload integration test needs: ``mikro`` provides the image/dataset
# API, ``rekuest`` is part of the default service registry that ``easy`` negotiates
# against. ``lok`` is always enabled (see ``REQUIRED_SERVICES``).
INTEGRATION_SERVICES = ["rekuest", "mikro", "kabinet"]

# lok auto-configures a local composition with this identifier from the default
# kommunity partners that ``arkitekt-server`` writes into the generated config.
# ``validatecode`` resolves the device code against it.
COMPOSITION_IDENTIFIER = "localhost"


@pytest.fixture(scope="session")
def arkitekt_server() -> Generator[ArkitektServer, None, None]:
    """Spin up an ephemeral Arkitekt server with the services needed for tests.

    Uses ``temp_setup`` which writes a throwaway config (anonymous volumes,
    randomized ports), builds a ``dokker`` testing deployment and pre-registers a
    health check for every enabled web service. The deployment is started here and
    torn down on teardown.
    """
    from arkitekt_server.dev import temp_setup

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

    The device-code login is auto-approved by running lok's ``validatecode``
    management command inside the lok container.
    """
    from fakts_next.grants.remote import FaktsEndpoint
    from arkitekt_next import easy
    from arkitekt_next.service_registry import get_default_service_registry

    async def device_code_hook(endpoint: FaktsEndpoint, device_code: str):
        await arkitekt_server.setup.arun(
            "lok",
            f"uv run python manage.py validatecode --code {device_code} "
            f"--user demo --org arkitektio --composition {COMPOSITION_IDENTIFIER}",
        )

    registry = get_default_service_registry()
    assert registry, "Service registry must be initialized"

    with easy(
        url=arkitekt_server.gateway_url,
        device_code_hook=device_code_hook,
    ) as app:
        yield AppWithinDeployment(server=arkitekt_server, app=app)
