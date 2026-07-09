"""Engine deployment profile configuration.

An **engine** is a standalone **deployer**: it runs on its own (in its own
docker-compose) and connects to an existing Arkitekt deployment (a hub, coord or
hubinator) to orchestrate app containers on its behalf. The deployer is therefore
NOT part of the hub profile -- only the hubinator bundles one inline; everywhere
else you run an engine.

It is a deep, standalone schema written to ``engine_config.yaml`` and consumed by
``diff.write_engine_files``.
"""

from pydantic import BaseModel, ConfigDict, Field

from arkitekt_next.server.device_id import get_or_set_device_id

from .infrastructure import DeployerConfig


class EngineConfig(BaseModel):
    """Configuration for a standalone engine (deployer) deployment."""

    device_id: str | None = Field(
        default_factory=get_or_set_device_id,
        description="Device ID for this engine instance",
    )
    url: str = Field(
        default="http://localhost",
        description="Gateway URL of the Arkitekt deployment the deployer connects to",
    )
    network: str = Field(
        default="arkitekt",
        description="Docker network the deployer joins -- must match the target "
        "deployment's internal network so spawned app containers can reach it",
    )
    organization: str = Field(
        default="arkitektio",
        description="Organization the deployer acts on behalf of",
    )
    instance_id: str = Field(
        default="default",
        description="Instance ID for the deployer",
    )
    default_service_grace_period_seconds: int = Field(
        default=2,
        description="Grace period before shutting the deployer down",
    )
    deployer: DeployerConfig = Field(default_factory=DeployerConfig)

    model_config = ConfigDict(extra="forbid")
