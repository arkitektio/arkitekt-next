from arkitekt_next.apps.service.fakts_next import (
    build_arkitekt_next_redeem_fakts_next,
)
from arkitekt_next.apps.service.fakts_qt import build_arkitekt_next_qt_fakts
from arkitekt_next.apps.service.herre_qt import build_arkitekt_next_qt_herre
from arkitekt_next.utils import create_arkitekt_next_folder
from arkitekt_next.model import Manifest
from arkitekt_next.apps.types import App
from arkitekt_next.service_registry import (
    ServiceBuilderRegistry,
    check_and_import_services,
)
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL
from qtpy import QtWidgets, QtCore
from typing import List, Optional
import os
import logging


def publicqt(
    identifier: str,
    version: str = "latest",
    logo: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    log_level: str = "ERROR",
    registry: Optional[ServiceBuilderRegistry] = None,
    parent: Optional[QtWidgets.QWidget] = None,
    beacon_widget: Optional[QtWidgets.QWidget] = None,
    login_widget: Optional[QtWidgets.QWidget] = None,
    settings: Optional[QtCore.QSettings] = None,
    **kwargs,
) -> App:
    """Public QtApp creation

    A simple way to create an Arkitekt app with a public grant (allowing users to sign
    in with the application ) utlizing a retrieve grant (necessating a previous configuration
    of the application on the server side)

    Args:
        identifier (str): The apps identifier
        version (str, optional): The apps verion. Defaults to "latest".
        parent (QtWidget, optional): The QtParent (for the login and server select widget). Defaults to None.

    Returns:
        Arkitekt: The Arkitekt app
    """

    registry = registry or check_and_import_services()

    settings = settings or QtCore.QSettings("arkitekt_next", f"{identifier}:{version}")

    manifest = Manifest(
        version=version,
        identifier=identifier,
        scopes=scopes if scopes else ["openid"],
        logo=logo,
        requirements=registry.get_requirements(),
    )

    fakts = build_arkitekt_next_qt_fakts(
        manifest=manifest,
        beacon_widget=beacon_widget,
        parent=parent,
        settings=settings,
    )

    herre = build_arkitekt_next_qt_herre(
        manifest,
        fakts=fakts,
        login_widget=login_widget,
        parent=parent,
        settings=settings,
    )

    params = kwargs

    try:
        from rich.logging import RichHandler

        logging.basicConfig(level=log_level, handlers=[RichHandler()])
    except ImportError:
        logging.basicConfig(level=log_level)

    app = App(
        fakts=fakts,
        herre=herre,
        manifest=manifest,
        services=registry.build_service_map(
            fakts=fakts, herre=herre, params=params, manifest=manifest
        ),
    )

    app.enter()

    return app
