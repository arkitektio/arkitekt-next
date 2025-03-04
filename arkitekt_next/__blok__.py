from arkitekt_next.bloks.admin import AdminBlok
from arkitekt_next.bloks.arkitekt import ArkitektBlok
from arkitekt_next.bloks.mikro import MikroBlok
from arkitekt_next.bloks.fluss import FlussBlok
from arkitekt_next.bloks.orkestrator import OrkestratorBlok
from arkitekt_next.bloks.redis import RedisBlok
from arkitekt_next.bloks.gateway import CaddyBlok
from arkitekt_next.bloks.livekit import LocalLiveKitBlok
from arkitekt_next.bloks.postgres import PostgresBlok
from arkitekt_next.bloks.minio import MinioBlok
from arkitekt_next.bloks.kabinet import KabinetBlok
from arkitekt_next.bloks.lok import LokBlok
from arkitekt_next.bloks.config import ConfigBlok
from arkitekt_next.bloks.mount import MountBlok
from arkitekt_next.bloks.internal_docker import InternalDockerBlok
from arkitekt_next.bloks.socket import DockerSocketBlok
from arkitekt_next.bloks.rekuest import RekuestBlok
from arkitekt_next.bloks.tailscale import TailscaleBlok
from arkitekt_next.bloks.secret import SecretBlok
from arkitekt_next.bloks.namegen import PreformedNamesBlok
from arkitekt_next.bloks.ollama import OllamaBlok
from arkitekt_next.bloks.self_signed import SelfSignedBlok
from arkitekt_next.bloks.kraph import KraphBlok
from arkitekt_next.bloks.local_sign import LocalSignBlok
from arkitekt_next.bloks.elektro import ElektroBlok


def get_bloks():
    return [
        AdminBlok(),
        ArkitektBlok(),
        MikroBlok(),
        FlussBlok(),
        RedisBlok(),
        CaddyBlok(),
        LocalLiveKitBlok(),
        PostgresBlok(),
        MinioBlok(),
        OllamaBlok(),
        LokBlok(),
        SelfSignedBlok(),
        KabinetBlok(),
        MountBlok(),
        ConfigBlok(),
        KraphBlok(),
        InternalDockerBlok(),
        DockerSocketBlok(),
        RekuestBlok(),
        TailscaleBlok(),
        SecretBlok(),
        PreformedNamesBlok(),
        OrkestratorBlok(),
        LocalSignBlok(),
        ElektroBlok(),
    ]

