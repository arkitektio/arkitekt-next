from fakts_next.fakts import Fakts
from typing import Optional
from fakts_next.grants.remote import RemoteGrant
from fakts_next.grants.remote.demanders.device_code import DeviceCodeDemander

from fakts_next.grants.remote.claimers.post import ClaimEndpointClaimer
from fakts_next.grants.remote.discovery.qt.selectable_beacon import (
    SelectBeaconWidget,
    QtSelectableDiscovery,
)
from arkitekt_next.base_models import Manifest
from qtpy import QtCore, QtWidgets
from fakts_next.cache.qt.settings import QtSettingsCache


class ArkitektNextFaktsQtRemoteGrant(RemoteGrant):
    """An ArkitektNext Fakts grant that uses Qt widgets for token and endpoint storage"""

    discovery: QtSelectableDiscovery


class ArkitektNextFaktsQt(Fakts):
    """A Fakts that uses Qt widgets for token and endpoint storage"""

    grant: ArkitektNextFaktsQtRemoteGrant


def build_arkitekt_next_qt_fakts_next(
    manifest: Manifest,
    no_cache: Optional[bool] = False,
    beacon_widget: Optional[QtWidgets.QWidget] = None,
    parent: Optional[QtWidgets.QWidget] = None,
    settings: Optional[QtCore.QSettings] = None,
) -> ArkitektNextFaktsQt:
    beacon_widget = beacon_widget or SelectBeaconWidget(
        parent=parent, settings=settings
    )

    return ArkitektNextFaktsQt(
        grant=ArkitektNextFaktsQtRemoteGrant(
            demander=DeviceCodeDemander(
                manifest=manifest,
                redirect_uri="http://127.0.0.1:6767",
                open_browser=True,
                requested_client_kind="desktop",
            ),
            discovery=QtSelectableDiscovery(
                widget=beacon_widget,
                settings=settings,
                allow_appending_slash=True,
                auto_protocols=["http", "https"],
                additional_beacons=["http://localhost"],
            ),
            claimer=ClaimEndpointClaimer(),
        ),
        cache=QtSettingsCache(settings=settings),
    )
