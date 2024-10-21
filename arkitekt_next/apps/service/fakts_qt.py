from fakts.fakts import Fakts
from typing import Optional
from fakts.grants.remote import RemoteGrant
from fakts.grants.remote.demanders.auto_save import AutoSaveDemander
from fakts.grants.remote.demanders.device_code import DeviceCodeDemander
from fakts.grants.remote.discovery.auto_save import AutoSaveDiscovery
from fakts.grants.remote.discovery.qt.auto_save_endpoint_widget import (
    AutoSaveEndpointWidget,
)
from fakts.grants.remote.discovery.qt.qt_settings_endpoint_store import (
    QtSettingsEndpointStore,
)
from fakts.grants.remote.demanders.qt.qt_settings_token_store import QTSettingTokenStore

from fakts.grants.remote.demanders.retrieve import RetrieveDemander
from fakts.grants.remote.claimers.post import ClaimEndpointClaimer
from fakts.grants.remote.discovery.qt.selectable_beacon import (
    SelectBeaconWidget,
    QtSelectableDiscovery,
)
from arkitekt_next.base_models import Manifest
from qtpy import QtCore, QtWidgets


class ArkitektNextFaktsAutoSaveDiscovery(AutoSaveDiscovery):
    """An ArkitektNext Fakts discovery that uses Qt widgets for token and endpoint storage"""

    discovery: QtSelectableDiscovery


class ArkitektNextFaktsQtRemoteGrant(RemoteGrant):
    """An ArkitektNext Fakts grant that uses Qt widgets for token and endpoint storage"""

    discovery: ArkitektNextFaktsAutoSaveDiscovery


class ArkitektNextFaktsQt(Fakts):
    """A Fakts that uses Qt widgets for token and endpoint storage"""

    grant: ArkitektNextFaktsQtRemoteGrant


def build_arkitekt_next_qt_fakts(
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
            demander=AutoSaveDemander(
                store=QTSettingTokenStore(
                    settings=settings,
                    save_key="fakts_token",
                ),
                demander=DeviceCodeDemander(
                    manifest=manifest,
                    redirect_uri="http://127.0.0.1:6767",
                    open_browser=True,
                    requested_client_kind="desktop",
                ),
            ),
            discovery=ArkitektNextFaktsAutoSaveDiscovery(
                store=QtSettingsEndpointStore(
                    settings=settings,
                    save_key="fakts_endpoint",
                ),
                decider=AutoSaveEndpointWidget(
                    parent=parent,
                ),
                discovery=QtSelectableDiscovery(
                    widget=beacon_widget,
                    settings=settings,
                    allow_appending_slash=True,
                    auto_protocols=["http", "https"],
                    additional_beacons=["http://localhost"],
                ),
            ),
            claimer=ClaimEndpointClaimer(),
        )
    )
