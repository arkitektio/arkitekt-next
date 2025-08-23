from typing import Generator
import pytest
from arkitekt_next.cli.main import cli
from click.testing import CliRunner
from arkitekt_server.create import temp_server, ArkitektServerConfig
from dokker import Deployment
from dataclasses import dataclass
from arkitekt_next.app import App
from fakts_next.grants.remote import FaktsEndpoint
from arkitekt_next import easy
from dokker import local

from arkitekt_next.service_registry import get_default_service_registry
import pytest

def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command line options for pytest."""
    parser.addoption(
        "--test-against",
        action="store",
        default="temp",
        help="Base URL of the Arkitekt server to use in tests",
    )


@pytest.fixture(scope="session")
def running_server(request: pytest.FixtureRequest) -> Generator[Deployment, None, None]:
    """ Generates a local Arkitekt server deployment for testing purposes. """
    
    if not request.config.getoption("--test-against") == "temp":
        raise ValueError("Invalid test environment specified. Currently only 'temp' is supported.")

    config = ArkitektServerConfig()

    with temp_server() as temp_path:
        
        setup = local(temp_path / "docker-compose.yaml")
        
        setup.add_health_check(
            url=lambda spec: f"http://localhost:{spec.find_service('gateway').get_port_for_internal(80).published}/lok/ht",
            service="lok",
            timeout=5,
            max_retries=10,
        )
        with setup as setup:
            setup.down()
            
            
            setup.up()
            
            setup.check_health()
            yield setup
            setup.down()
 
 
 
@dataclass
class EasyApp:
    """Dataclass to hold the Arkitekt server deployment."""
    deployment: Deployment
    app: App         
            

@pytest.fixture(scope="session")
def test_app(running_server: Deployment) -> Generator[EasyApp, None, None]:
    """Fixture to ensure the Arkitekt server is running."""
    
    async def device_code_hook(endpoint: FaktsEndpoint, device_code: str):
        
        await running_server.arun(
            "lok", f"uv run python manage.py validatecode {device_code} --user demo --org arkitektio"
        )
        
        
    registry = get_default_service_registry()
        
    assert registry, "Service registry must be initialized"    
        


    with easy(url=f"http://localhost:{running_server.spec.find_service('gateway').get_port_for_internal(80).published}", device_code_hook=device_code_hook) as app:
        
        yield EasyApp(
            deployment=running_server,
            app=app
        )