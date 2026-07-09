from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Literal
from arkitekt_next.server.diff import (
    write_virtual_config_files,
    write_hub_files,
    write_coord_files,
    write_engine_files,
    iterate_service,
)
from .config import ArkitektServerConfig, HubConfig, CoordConfig, EngineConfig
from .services import SERVICE_REGISTRY
from pathlib import Path
import random
from dokker import Deployment, testing
from dataclasses import dataclass

if TYPE_CHECKING:
    from arkitekt_next.server.lok import LokController

# Services that are always enabled regardless of the requested selection.
# Lok provides authentication/authorization and every other service depends on it.
REQUIRED_SERVICES = {"lok"}

# Release channels that select the image tag for the Arkitekt services.
Channel = Literal["next", "latest"]


def _retag_image(image: str, tag: str) -> str:
    """Replace the tag of a docker image reference, preserving registry/repository.

    ``jhnnsrs/mikro:dev`` -> ``jhnnsrs/mikro:<tag>``. If the image has no tag, one
    is appended. A ``:`` in a registry host (e.g. ``host:5000/img``) is ignored.
    """
    # Only treat a colon in the final path segment as a tag separator.
    if ":" in image.rsplit("/", 1)[-1]:
        base = image.rsplit(":", 1)[0]
    else:
        base = image
    return f"{base}:{tag}"


def create_server(path: Path | str, config: ArkitektServerConfig | None = None):
    """
    Create a server configuration at the specified path using the provided config.

    Args:
        path (str): The path where the server configuration will be created.
        config (ArkitektServerConfig): The configuration for the server.

    Returns:
        None
    """
    if isinstance(path, str):
        path = Path(path)

    # Ensure the directory exists
    path.mkdir(parents=True, exist_ok=True)

    if config is None:
        config = ArkitektServerConfig()

    # Write the configuration to a file
    write_virtual_config_files(path, config)


def create_hub_server(path: Path | str, config: HubConfig | None = None) -> None:
    """Generate a hub deployment (services, no local coordinator) at ``path``."""
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if config is None:
        config = HubConfig()
    write_hub_files(path, config)


def create_coord_server(path: Path | str, config: CoordConfig | None = None) -> None:
    """Generate a coordinator deployment (Lok + Kontrol only) at ``path``."""
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if config is None:
        config = CoordConfig()
    write_coord_files(path, config)


def create_engine_server(path: Path | str, config: EngineConfig | None = None) -> None:
    """Generate a standalone engine (deployer) deployment at ``path``."""
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if config is None:
        config = EngineConfig()
    write_engine_files(path, config)


def create_test_config(
    services: list[str] | None = None,
    *,
    config: ArkitektServerConfig | None = None,
    channel: Channel | None = None,
    randomize_ports: bool = True,
) -> ArkitektServerConfig:
    """Build an ``ArkitektServerConfig`` suitable for ephemeral/test deployments.

    This enables only the requested services (plus the always-required ones, see
    ``REQUIRED_SERVICES``) and disables the rest. It also hardens the config for
    throwaway use by switching the database and object store to anonymous docker
    volumes (instead of bind mounts) and randomizing the exposed gateway ports so
    multiple deployments can run in parallel without clashing.

    Args:
        services: Identifiers of the services to enable (e.g. ``["rekuest", "mikro"]``).
            Must be keys of ``SERVICE_REGISTRY``. If ``None``, the config's existing
            enabled flags are left untouched.
        config: A base config to mutate. A fresh ``ArkitektServerConfig`` is created
            if not provided.
        channel: Release channel selecting the service image tag -- ``"next"`` or
            ``"latest"`` retags every Arkitekt service image accordingly. If ``None``
            (the default), each service keeps its configured image/version.
        randomize_ports: Whether to assign random exposed gateway ports.

    Returns:
        The configured ``ArkitektServerConfig``.
    """
    config = config or ArkitektServerConfig()

    if services is not None:
        unknown = set(services) - set(SERVICE_REGISTRY)
        if unknown:
            raise ValueError(
                f"Unknown service(s): {sorted(unknown)}. "
                f"Available services: {sorted(SERVICE_REGISTRY)}"
            )

        wanted = set(services) | REQUIRED_SERVICES
        for name in SERVICE_REGISTRY:
            getattr(config, name).enabled = name in wanted

    if channel is not None:
        # Switch every Arkitekt service image to the requested release channel.
        # Some services (e.g. lovekit) have no configurable image and are skipped.
        for name in SERVICE_REGISTRY:
            service = getattr(config, name)
            if getattr(service, "image", None) is not None:
                service.image = _retag_image(service.image, channel)

    # The deployer needs the docker socket and registers itself against a running
    # gateway; it is irrelevant for service tests and only adds a crash-looping
    # container, so disable it for throwaway deployments.
    config.deployer.enabled = False

    # Make sure we are creating volumes not bind mounts, so nothing lingers on disk.
    config.minio.mount = None
    config.db.mount = None

    if randomize_ports:
        config.gateway.exposed_http_port = random.randint(8000, 9000)
        config.gateway.exposed_https_port = random.randint(9000, 10000)

    return config


@contextmanager
def temp_server(
    config: ArkitektServerConfig | None = None,
) -> Generator[Path, None, None]:
    """
    Create a temporary server configuration using the provided config.

    This is a context manager that yields the path to the temporary server configuration.
    The server directory is created and cleaned up automatically.

    Attention: The docker compose project that was created will not be cleaned up automatically.
                If you want to clean it up, you have to call `down` on the project manually.
                Or use the `local` function from the `dokker` package to create a local deployment.

    Args:
        config (ArkitektServerConfig): The configuration for the server.

    Yield:
        Path: The path to the temporary server configuration.
    """
    import tempfile

    config = create_test_config(config=config)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        create_server(temp_path, config)
        yield temp_path


@dataclass
class ArkitektServer:
    """Handle to a generated Arkitekt deployment for use in tests.

    Wraps the generated config, the directory it was written to and a (not yet
    started) ``dokker`` deployment with health checks pre-registered for every
    enabled web service. The caller is responsible for the docker lifecycle::

        with srv.setup:
            srv.setup.up()
            srv.setup.check_health()
            ...
    """

    config: ArkitektServerConfig
    deployment: Deployment
    path: Path

    @property
    def setup(self) -> Deployment:
        """The underlying ``dokker`` deployment (alias for ``deployment``)."""
        return self.deployment

    @property
    def enabled_services(self) -> list[str]:
        """Identifiers of the services actually deployed (enabled and deployable).

        Mirrors ``diff.iterate_service`` -- e.g. ``lovekit`` is enabled by default
        but has no image and is not deployed, so it is not listed here.
        """
        return [service.get_identifier() for service in iterate_service(self.config)]

    def get_service_url(
        self, service_name: str, internal_port: int = 80, protocol: str = "http"
    ) -> str:
        """Get the URL for a service."""
        service = self.deployment.spec.find_service(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found")

        port = service.get_port_for_internal(internal_port)
        if not port:
            raise ValueError(
                f"Service {service_name} does not expose internal port {internal_port}"
            )

        return f"{protocol}://localhost:{port.published}"

    @property
    def gateway_url(self) -> str:
        """Get the URL for the gateway service."""
        return self.get_service_url("gateway", 80)

    @property
    def lok(self) -> "LokController":
        """Controller for the deployment's lok (coordination) server.

        Lets tests act as the human operator: approve/deny device codes,
        authorize hub registrations, or run arbitrary management
        commands inside the lok container.
        """
        from arkitekt_next.server.lok import LokController

        return LokController(self.deployment)

    def health_url(self, service: str) -> str:
        """Get the gateway-routed health-check URL for a service (``/<service>/ht``)."""
        return f"{self.gateway_url}/{service}/ht"

    def graphql_url(self, service: str) -> str:
        """Get the gateway-routed GraphQL endpoint URL for a service."""
        return f"{self.gateway_url}/{service}/graphql"


# Backwards-compatibility alias for the previous name.
TempDeployment = ArkitektServer


def _register_health_checks(setup: Deployment, config: ArkitektServerConfig) -> None:
    """Register a gateway-routed ``/<host>/ht`` health check per enabled web service.

    Uses ``iterate_service`` as the source of truth for which services are actually
    deployed as web/Django services. Note that ``lovekit`` is intentionally not part
    of ``iterate_service`` (it is a LiveKit/realtime service, not a Django app), so
    it is not deployed and gets no health check.
    """
    for service in iterate_service(config):
        host = service.host
        # Bind ``host`` via default arg to avoid late-binding closure capture.
        setup.add_health_check(
            url=lambda spec, host=host: (
                f"http://localhost:"
                f"{setup.spec.find_service('gateway').get_port_for_internal(80).published}"
                f"/{host}/ht"
            ),
            service=host,
            # First boot runs database migrations, which can take a while.
            timeout=10,
            max_retries=60,
        )


@contextmanager
def temp_setup(
    services: list[str] | None = None,
    *,
    config: ArkitektServerConfig | None = None,
    channel: Channel | None = None,
    health_checks: bool = True,
) -> Generator[ArkitektServer, None, None]:
    """Generate a temporary Arkitekt deployment and yield a handle to it.

    The configuration is written to a temporary directory and a ``dokker`` testing
    deployment is built with health checks registered for every enabled web service.
    The deployment is **not** started -- the caller decides when to ``up()``/``down()``.
    The temporary directory is removed when the context exits, and the ``testing``
    teardown policy ensures the docker compose project is torn down if it was started.

    Args:
        services: Identifiers of the services to enable. See ``create_test_config``.
        config: An optional base config to mutate.
        channel: Release channel for the service images (``"next"``/``"latest"``/``None``).

    Yield:
        ArkitektServer: A handle exposing the config, path, and dokker ``setup``.
    """
    import tempfile

    config = create_test_config(services, config=config, channel=channel)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        create_server(temp_path, config)

        # ``testing`` defaults to the "testing" teardown policy, which already
        # downs the stack (removing volumes/orphans) and tears the project down
        # on context exit -- no explicit down_on_exit flag is needed.
        setup = testing(temp_path / "docker-compose.yaml")

        if health_checks:
            _register_health_checks(setup, config)

        yield ArkitektServer(config=config, deployment=setup, path=temp_path)


@contextmanager
def temp_deployment(
    config: ArkitektServerConfig | None = None,
) -> Generator[ArkitektServer, None, None]:
    """
    Create a temporary deployment configuration using the provided config.

    This is a context manager that yields the path to the temporary deployment configuration.
    The deployment directory is created and cleaned up automatically.

    Args:
        config (ArkitektServerConfig): The configuration for the deployment.
    Yield:

    """

    # Preserve historical behaviour: bring the deployment up without registering
    # health checks (the caller may inspect/down it directly).
    with temp_setup(config=config, health_checks=False) as server:
        setup = server.setup
        with setup:
            # Check that the setup can be initialized
            assert setup is not None, "Setup could not be initialized"

            # Entering the deployment no longer inspects automatically, so populate
            # the compose spec before reading it via ``setup.spec``.
            setup.inspect()

            # The gateway is always present, and every deployed service should be too.
            assert setup.spec.find_service("gateway") is not None, (
                "Gateway service not found"
            )
            for service in iterate_service(server.config):
                assert setup.spec.find_service(service.host) is not None, (
                    f"{service.get_identifier()} service not found"
                )

            yield server

            setup.down()
