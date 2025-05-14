from typing import Optional

from fakts_next.fakts import Fakts
from fakts_next.grants.remote import RemoteGrant
from fakts_next.grants.remote.discovery.well_known import WellKnownDiscovery
from fakts_next.grants.remote.demanders.static import StaticDemander
from fakts_next.grants.remote.demanders.device_code import (
    ClientKind,
    DeviceCodeDemander,
)
from fakts_next.grants.remote.claimers.post import ClaimEndpointClaimer
from fakts_next.grants.remote.demanders.redeem import RedeemDemander
from fakts_next.cache.file import FileCache
from arkitekt_next.base_models import Manifest


def build_arkitekt_next_fakts_next(
    manifest: Manifest,
    url: Optional[str] = None,
    no_cache: bool = False,
    headless: bool = False,
) -> Fakts:
    identifier = manifest.identifier
    version = manifest.version
    if url is None:
        raise ValueError("URL must be provided")

    demander = DeviceCodeDemander(
        manifest=manifest,
        open_browser=not headless,
        requested_client_kind=ClientKind.DEVELOPMENT,
    )

    return Fakts(
        grant=RemoteGrant(
            demander=demander,
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
        ),
    )


def build_arkitekt_next_redeem_fakts_next(manifest: Manifest, redeem_token: str, url: str) -> Fakts:
    identifier = manifest.identifier
    version = manifest.version

    return Fakts(
        grant=RemoteGrant(
            demander=RedeemDemander(token=redeem_token, manifest=manifest),
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
        ),
    )


def build_arkitekt_next_token_fakts_next(
    manifest: Manifest,
    token: str,
    url: str,
):
    identifier = manifest.identifier
    version = manifest.version

    return Fakts(
        grant=RemoteGrant(
            demander=StaticDemander(token=token),  # type: ignore
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
        ),
    )

