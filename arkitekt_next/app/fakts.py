from typing import Optional

from fakts_next.fakts import Fakts
from fakts_next.grants.remote import RemoteGrant
from fakts_next.grants.remote.discovery.well_known import WellKnownDiscovery
from fakts_next.grants.remote.demanders.static import StaticDemander
from fakts_next.grants.remote.demanders.device_code import (
    ClientKind,
    DeviceCodeDemander,
    DeviceCodeHook,
    display_in_terminal,
    
)
from fakts_next.grants.remote.claimers.post import ClaimEndpointClaimer
from fakts_next.grants.remote.demanders.redeem import RedeemDemander
from fakts_next.cache.file import FileCache
from fakts_next.models import Manifest


def build_device_code_fakts(
    manifest: Manifest,
    url: Optional[str] = None,
    no_cache: bool = False,
    headless: bool = False,
    device_code_hook: Optional[DeviceCodeHook] = None,
) -> Fakts:
    """ Builds a Fakts instance for device code authentication.
    
    This is used when the user wants to authenticate an application
    using a device code. The user will be prompted to open a browser
    and enter a code to authenticate the application.
    
    
    
    """
    identifier = manifest.identifier
    version = manifest.version
    if url is None:
        raise ValueError("URL must be provided")

    demander = DeviceCodeDemander(
        manifest=manifest,
        open_browser=not headless,
        requested_client_kind=ClientKind.DEVELOPMENT,
        device_code_hook=device_code_hook if device_code_hook else display_in_terminal,
    )

    return Fakts(
        grant=RemoteGrant(
            demander=demander,
            discovery=WellKnownDiscovery(url=url, auto_protocols=["https", "http"]),
            claimer=ClaimEndpointClaimer(),
        ),
        manifest=manifest,
        cache=FileCache(
            cache_file=f".arkitekt_next/cache/{identifier}-{version}_fakts_cache.json",
            hash=manifest.hash() + url,
        ),
    )


def build_redeem_fakts(manifest: Manifest, redeem_token: str, url: str) -> Fakts:
    """ Builds a Fakts instance for redeeming a token.
    
    A redeem token is used to register an application with the
    fakts server, and to claim the configuration for the application.
    
    Instead of using a device code, the user can redeem an application
    without user interaction.
    
    """
    identifier = manifest.identifier
    version = manifest.version

    return Fakts(
        manifest=manifest,
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


def build_token_fakts(
    manifest: Manifest,
    token: str,
    url: str,
) -> Fakts:
    """ Builds a Fakts instance for token-based authentication.
    
    This is used when an appllication was previously authenticated
    and the user has a (claim) token to use for authentication.
    
    E.g. when deploying an application through the kabinet deployer
    
    """
    identifier = manifest.identifier
    version = manifest.version

    return Fakts(
        manifest=manifest,
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
