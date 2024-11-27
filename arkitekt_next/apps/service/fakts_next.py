from typing import Optional

from fakts_next.fakts import Fakts
from fakts_next.grants.remote import RemoteGrant
from fakts_next.grants.remote.discovery.well_known import WellKnownDiscovery
from fakts_next.grants.remote import RemoteGrant
from fakts_next.grants.remote.demanders.static import StaticDemander
from fakts_next.grants.remote.demanders.device_code import DeviceCodeDemander
from fakts_next.grants.remote.claimers.post import ClaimEndpointClaimer
from fakts_next.grants.remote.demanders.redeem import RedeemDemander
from fakts_next.cache.file import FileCache
from arkitekt_next.base_models import Manifest


class ArkitektNextFaktsQt(Fakts):
    grant: RemoteGrant


class ArkitektNextFaktsNext(Fakts):
    pass


def build_arkitekt_next_fakts_next(
    manifest: Manifest,
    url: Optional[str] = None,
    no_cache: bool = False,
    headless: bool = False,
    client_kind: str = "development",
) -> ArkitektNextFaktsNext:
    identifier = manifest.identifier
    version = manifest.version

    demander = DeviceCodeDemander(
        manifest=manifest,
        redirect_uri="http://127.0.0.1:6767",
        open_browser=not headless,
        requested_client_kind=client_kind,
    )

    return ArkitektNextFaktsNext(
        grant=RemoteGrant(
            demander=demander,
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
            skip_cache=no_cache,
        ),
    )


def build_arkitekt_next_redeem_fakts_next(
    manifest: Manifest,
    redeem_token: str,
    url,
    no_cache: Optional[bool] = False,
    headless=False,
):
    identifier = manifest.identifier
    version = manifest.version

    return ArkitektNextFaktsNext(
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
    url,
):
    identifier = manifest.identifier
    version = manifest.version

    return ArkitektNextFaktsNext(
        grant=RemoteGrant(
            demander=StaticDemander(token=token),
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
        ),
    )
