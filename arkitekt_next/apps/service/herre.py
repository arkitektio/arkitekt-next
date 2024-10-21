from herre.herre import Herre
from fakts import Fakts
from herre.grants.oauth2.refresh import RefreshGrant
from herre.fakts.fakts_endpoint_fetcher import FaktsUserFetcher
from herre.fakts.grant import FaktsGrant
from arkitekt_next.base_models import User
from arkitekt_next.apps.service.grant_registry import ARKITEKT_GRANT_REGISTRY


class ArkitektNextHerre(Herre):
    pass


def build_arkitekt_next_herre(fakts: Fakts) -> ArkitektNextHerre:
    return ArkitektNextHerre(
        grant=RefreshGrant(
            grant=FaktsGrant(
                fakts=fakts, fakts_group="lok", grant_registry=ARKITEKT_GRANT_REGISTRY
            ),
        ),
        fetcher=FaktsUserFetcher(
            fakts=fakts, fakts_key="lok.userinfo_url", userModel=User
        ),
    )
