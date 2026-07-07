"""Configuration package for Arkitekt Server.

This package provides all configuration models for the Arkitekt platform,
organized into logical modules:

- types: Discriminated union types for configuration options
- utils: Utility functions for config generation
- base: Base classes and protocols for services
- infrastructure: Infrastructure services (DB, Redis, MinIO, Gateway)
- users: User, Organization, and Membership models
- kommunity: Kommunity partner models for external integrations
- server: Main ArkitektServerConfig and Setup classes
"""

# Re-export all types for convenient access
from .types import (
    # Bucket configurations
    BucketConfig,
    LocalBucketConfig,
    S3BucketConfig,
    # Database configurations
    DBConfig,
    LocalDBConfig,
    RemoteDBConfig,
    # Admin configurations
    AdminConfig,
    GlobalAdminConfig,
    SpecificAdminConfig,
    # Redis configurations
    RedisConfig,
    LocalRedisConfig,
    RemoteRedisConfig,
    # ChromaDB configurations
    ChromaDBConfig,
    LocalChromaDBConfig,
    RemoteChromaDBConfig,
    # Ollama configurations
    OllamaConfig,
    LocalOllamaConfig,
    RemoteOllamaConfig,
    # Auth configurations
    AuthConfig,
    LocalAuthConfig,
    StaticTokenAuthConfig,
    # Path configurations
    PathConfig,
    LocalPath,
    ForcePath,
)

# Re-export utility functions
from .utils import (
    KeyPair,
    build_ed25519_key_pair,
    build_key_pair,
    generate_alpha_numeric_string,
    generate_django_secret_key,
    generate_name,
)

# Re-export base classes (without BaseServiceConfig to avoid duplication)
from .base import (
    AdditionalAppConfig,
    AppProtocol,
    BaseAppConfig,
    BaseStackConfig,
    ServiceProtocol,
)

# Re-export infrastructure configs
from .infrastructure import (
    DatenConfig,
    DeployerConfig,
    GatewayConfig,
    MinioConfig,
    RedisServiceConfig,
)

# Re-export user models
from .users import (
    EmailConfig,
    Membership,
    Organization,
    Role,
    User,
    create_default_memberships,
    create_default_organization,
    create_default_users,
)

# Re-export kommunity models
from .kommunity import (
    KommunityPartner,
    PreconfiguredComposition,
    ServiceAlias,
    ServiceInstance,
    ServiceManifest,
    create_default_kommunity_partners,
    create_local_service_aliases,
)

# Re-export server config
from .server import (
    ArkitektServerConfig,
    Setup,
)

# Re-export the deep, standalone deployment-profile schemas (hub / coord). The
# hubinator profile reuses ArkitektServerConfig above.
from .hub import HubConfig
from .coord import CoordConfig
from .engine import EngineConfig


# Lazy import for BaseServiceConfig from services to avoid circular imports
def __getattr__(name: str):
    if name in ("BaseServiceConfig", "BaseService"):
        from arkitekt_next.server.services.base import BaseServiceConfig

        return BaseServiceConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Types
    "BucketConfig",
    "LocalBucketConfig",
    "S3BucketConfig",
    "DBConfig",
    "LocalDBConfig",
    "RemoteDBConfig",
    "AdminConfig",
    "GlobalAdminConfig",
    "SpecificAdminConfig",
    "RedisConfig",
    "LocalRedisConfig",
    "RemoteRedisConfig",
    "ChromaDBConfig",
    "LocalChromaDBConfig",
    "RemoteChromaDBConfig",
    "OllamaConfig",
    "LocalOllamaConfig",
    "RemoteOllamaConfig",
    "AuthConfig",
    "LocalAuthConfig",
    "StaticTokenAuthConfig",
    "PathConfig",
    "LocalPath",
    "ForcePath",
    # Utils
    "KeyPair",
    "build_key_pair",
    "build_ed25519_key_pair",
    "generate_alpha_numeric_string",
    "generate_django_secret_key",
    "generate_name",
    # Base
    "ServiceProtocol",
    "AppProtocol",
    "BaseServiceConfig",
    "BaseAppConfig",
    "AdditionalAppConfig",
    "BaseStackConfig",
    "BaseService",  # Backwards compatibility alias
    # Infrastructure
    "MinioConfig",
    "DatenConfig",
    "RedisServiceConfig",
    "GatewayConfig",
    "DeployerConfig",
    # Users
    "User",
    "Membership",
    "Organization",
    "Role",
    "EmailConfig",
    "create_default_organization",
    "create_default_users",
    "create_default_memberships",
    # Kommunity
    "ServiceAlias",
    "ServiceManifest",
    "ServiceInstance",
    "PreconfiguredComposition",
    "KommunityPartner",
    "create_local_service_aliases",
    "create_default_kommunity_partners",
    # Server
    "ArkitektServerConfig",
    "Setup",
    # Deployment profiles
    "HubConfig",
    "CoordConfig",
    "EngineConfig",
]
