from arkitekt_next_next.apps.fallbacks import ImportException
from arkitekt_next_next.apps.service.fakts_next import (
    build_arkitekt_next_fakts_next,
    build_arkitekt_next_redeem_fakts_next,
)
from arkitekt_next_next.apps.service.herre import build_arkitekt_next_herre
from arkitekt_next_next.model import Manifest

from .types import NextApp


def build_next_app(
    manifest: Manifest,
    url=None,
    no_cache=False,
    headless=False,
    instance_id=None,
    token=None,
    app_kind="development",
    redeem_token=None,
):
    if redeem_token:
        fakts = build_arkitekt_next_redeem_fakts_next(
            manifest=manifest,
            redeem_token=redeem_token,
            url=url,
            no_cache=no_cache,
            headless=headless,
        )
    else:
        fakts = build_arkitekt_next_fakts_next(
            manifest=manifest,
            url=url,
            no_cache=no_cache,
            headless=headless,
            client_kind=app_kind,
        )

    herre = build_arkitekt_next_herre(fakts=fakts)
