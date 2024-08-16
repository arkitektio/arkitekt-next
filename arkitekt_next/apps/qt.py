from arkitekt_next_next.model import Manifest
from arkitekt_next_next.apps.types import QtApp
from arkitekt_next_next.apps.fallbacks import ImportException, InstallModuleException
from typing import Any, Optional


def build_arkitekt_next_qt_app(
    manifest: Manifest,
    no_cache: bool = False,
    instance_id: Optional[str] = None,
    beacon_widget: Any = None,
    login_widget: Any = None,
    parent: Any = None,
    settings: Any = None,
):
    try:
        from koil.composition.qt import QtPedanticKoil
        from qtpy import QtCore

        settings = settings or QtCore.QSettings()
    except ImportError as e:
        raise InstallModuleException(
            "Please install qtpy to use arkitekt_next_qt"
        ) from e

    try:
        from arkitekt_next_next.apps.service.fakts_qt import (
            build_arkitekt_next_qt_fakts,
        )

        fakts = build_arkitekt_next_qt_fakts(
            manifest=manifest,
            no_cache=no_cache,
            beacon_widget=beacon_widget,
            parent=parent,
            settings=settings,
        )
    except ImportError as e:
        fakts = ImportException(import_exception=e, install_library="qtpy")

    try:
        from arkitekt_next_next.apps.service.herre_qt import (
            build_arkitekt_next_qt_herre,
        )

        herre = build_arkitekt_next_qt_herre(
            manifest=manifest,
            fakts=fakts,
            login_widget=login_widget,
            parent=parent,
            settings=settings,
        )
    except ImportError as e:
        herre = ImportException(import_exception=e, install_library="qtpy")

    try:
        from arkitekt_next_next.apps.service.rekuest import build_arkitekt_next_rekuest

        rekuest = build_arkitekt_next_rekuest(
            fakts=fakts, herre=herre, instance_id=instance_id or "main"
        )
    except ImportError as e:
        rekuest = ImportException(import_exception=e, install_library="rekuest")

    try:
        from arkitekt_next_next.apps.service.mikro import build_arkitekt_next_mikro

        mikro = build_arkitekt_next_mikro(fakts=fakts, herre=herre)
    except ImportError as e:
        mikro = ImportException(import_exception=e, install_library="mikro")

    try:
        from arkitekt_next_next.apps.service.unlok import build_arkitekt_next_unlok

        unlok = build_arkitekt_next_unlok(herre=herre, fakts=fakts)
    except ImportError as e:
        unlok = ImportException(import_exception=e, install_library="unlok")

    try:
        from arkitekt_next_next.apps.service.fluss import build_arkitekt_next_fluss

        fluss = build_arkitekt_next_fluss(herre=herre, fakts=fakts)
    except ImportError as e:
        fluss = ImportException(import_exception=e, install_library="fluss")

    try:
        from arkitekt_next_next.apps.service.kluster import build_arkitekt_next_kluster

        kluster = build_arkitekt_next_kluster(herre=herre, fakts=fakts)
    except ImportError as e:
        kluster = ImportException(import_exception=e, install_library="kluster")

    return QtApp(
        koil=QtPedanticKoil(parent=parent),
        manifest=manifest,
        fakts=fakts,
        herre=herre,
        rekuest=rekuest,
        mikro=mikro,
        unlok=unlok,
        fluss=fluss,
        kluster=kluster,
    )
