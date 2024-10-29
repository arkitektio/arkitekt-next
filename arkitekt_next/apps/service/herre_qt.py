from herre_next.herre import Herre
from fakts_next import Fakts
from herre_next.grants.oauth2.refresh import RefreshGrant
from herre_next.fakts.grant import FaktsGrant
from herre_next.fakts.fakts_qt_store import FaktsQtStore

from herre_next.grants.auto_login import AutoLoginGrant
from herre_next.grants.qt.auto_login import AutoLoginWidget
from herre_next.fakts.fakts_endpoint_fetcher import FaktsUserFetcher
from arkitekt_next.base_models import Manifest, User
from arkitekt_next.apps.service.grant_registry import ARKITEKT_GRANT_REGISTRY


class ArkitektNextAutoLogin(AutoLoginGrant):
    store: FaktsQtStore
    fetcher: FaktsUserFetcher
    grant: FaktsGrant


class ArkitektNextRefreshGrant(RefreshGrant):
    grant: ArkitektNextAutoLogin


class ArkitektNextHerreQt(Herre):
    grant: ArkitektNextRefreshGrant


def build_arkitekt_next_qt_herre_next(
    manifest: Manifest,
    fakts: Fakts,
    login_widget=None,
    parent=None,
    settings=None,
):
    login_widget = login_widget or AutoLoginWidget(parent=parent)

    grant = ArkitektNextAutoLogin(
        store=FaktsQtStore(
            fakts=fakts,
            settings=settings,
            fakts_key="lok.endpoint_url",
        ),
        widget=login_widget,
        fetcher=FaktsUserFetcher(
            fakts=fakts, fakts_key="lok.userinfo_url", userModel=User
        ),
        grant=FaktsGrant(
            fakts=fakts, fakts_group="lok", grant_registry=ARKITEKT_GRANT_REGISTRY
        ),
    )

    return ArkitektNextHerreQt(
        grant=ArkitektNextRefreshGrant(grant=grant),
        fetcher=FaktsUserFetcher(
            fakts=fakts, fakts_key="lok.userinfo_url", userModel=User
        ),
    )
