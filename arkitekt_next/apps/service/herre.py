from herre_next.herre import Herre
from fakts_next import Fakts
from herre_next.grants.oauth2.refresh import RefreshGrant
from herre_next.fakts.fakts_endpoint_fetcher import FaktsUserFetcher
from herre_next.fakts.grant import FaktsGrant
from arkitekt_next.base_models import User
from arkitekt_next.apps.service.grant_registry import ARKITEKT_GRANT_REGISTRY


class ArkitektNextHerre(Herre):
    pass


def build_arkitekt_next_herre_next(fakts_next: Fakts) -> ArkitektNextHerre:
    return ArkitektNextHerre(
        grant=RefreshGrant(
            grant=FaktsGrant(
                fakts=fakts_next,
                fakts_group="lok",
                grant_registry=ARKITEKT_GRANT_REGISTRY,
            ),
        ),
        fetcher=FaktsUserFetcher(
            fakts=fakts_next, fakts_key="lok.userinfo_url", userModel=User
        ),
    )
