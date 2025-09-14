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



@pytest.fixture(scope="session")
def arkitekt_server() -> Generator[Deployment, None, None]:
    """ Generates a local Arkitekt server deployment for testing purposes. """
    
    
    config = ArkitektServerConfig()
    
    
    with temp_server() as temp_path:
        
        setup = local(temp_path / "docker-compose.yaml")
        
        setup.add_health_check(
            url=lambda spec: f"http://localhost:{spec.find_service('gateway').get_port_for_internal(80).published}/lok/ht",
            service="lok",
            timeout=5,
            max_retries=20,
        )
        with setup as setup:
            setup.down()
            
            
            setup.up()
            
            setup.check_health()
            yield setup
            setup.down()
 
 
 
@dataclass
class AppWithinDeployment:
    """Dataclass to hold the Arkitekt server deployment."""
    deployment: Deployment
    app: App         
            

@pytest.fixture(scope="session")
def running_app(arkitekt_server: Deployment) -> Generator[AppWithinDeployment, None, None]:
    """Fixture to ensure the Arkitekt server is running."""
    from mikro_next.api.schema import create_dataset
    
    async def device_code_hook(endpoint: FaktsEndpoint, device_code: str):
        
        await arkitekt_server.arun(
            "lok", f"uv run python manage.py validatecode {device_code} --user demo --org arkitektio"
        )
        
        
    registry = get_default_service_registry()
        
    assert registry, "Service registry must be initialized"    
        


    with easy(url=f"http://localhost:{arkitekt_server.spec.find_service('gateway').get_port_for_internal(80).published}", device_code_hook=device_code_hook) as app:
        
        yield AppWithinDeployment(
            deployment=arkitekt_server,
            app=app
        )