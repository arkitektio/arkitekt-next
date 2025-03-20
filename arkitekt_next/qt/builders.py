from arkitekt_next.apps.service.fakts_next import (
    build_arkitekt_next_redeem_fakts_next,
)
from arkitekt_next.apps.service.fakts_qt import build_arkitekt_next_qt_fakts_next
from arkitekt_next.apps.service.herre_qt import build_arkitekt_next_qt_herre_next
from arkitekt_next.utils import create_arkitekt_next_folder
from arkitekt_next.base_models import Manifest
from arkitekt_next.apps.types import App
from arkitekt_next.service_registry import (
    ServiceBuilderRegistry,
    get_default_service_registry,
)
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL
from qtpy import QtWidgets, QtCore
from typing import List, Optional
import os
import logging
from typing import List, Optional
import logging
import os
from arkitekt_next.qt.types import QtApp
from arkitekt_next.apps.service.fakts_next import (
    build_arkitekt_next_fakts_next,
    build_arkitekt_next_redeem_fakts_next,
    build_arkitekt_next_token_fakts_next,
)
from arkitekt_next.apps.service.herre import build_arkitekt_next_herre_next
from arkitekt_next.utils import create_arkitekt_next_folder
from arkitekt_next.base_models import Manifest
from arkitekt_next.apps.types import App
from arkitekt_next.service_registry import (
    ServiceBuilderRegistry,
)
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL


def devqt(
    identifier: str,
    version: str = "0.0.1",
    logo: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    url: str = DEFAULT_ARKITEKT_URL,
    headless: bool = False,
    log_level: str = "ERROR",
    parent: Optional[QtWidgets.QWidget] = None,
    token: Optional[str] = None,
    no_cache: bool = False,
    redeem_token: Optional[str] = None,
    app_kind: str = "development",
    registry: Optional[ServiceBuilderRegistry] = None,
    description: Optional[str] = None,
    **kwargs,
) -> QtApp:
    """Creates a next app

    A simple way to create an ArkitektNext Next app, ArkitektNext next apps are
    development apps by default, as they will try to register themselves
    with services that are not yet available in production (such as the
    rekuest_next and mikro_next services). They represent the next generation
    of ArkitektNext apps, and will be the default way to create ArkitektNext apps
    in the future. From here be dragons.

    A few things to note:
        -   The Next builder closely mimics the easy builder, but will use the
            next generation of services (such as rekuest_next and mikro_next)
            and will therefore not be compatible with the current generation.

        -  Next apps will try to establish themselves a "development" apps, by default
            which means that they will be authenticated with the ArkitektNext server on
            a per user basis. If you want to create a "desktop" app, which multiple users
            can use, you should set the `app_kind` to "desktop" TODO: Currently not implemented (use next app for this)
        -  The Next builder can also be used in plugin apps, and when provided with a fakts_next token
           will be able to connect to the ArkitektNext server without any user interaction.


    Parameters
    ----------
    identifier : str
        The apps identifier (should be globally unique, see Manifest for more info)
    version : str, optional
        The version of the app, by default "0.0.1"
    logo : str, optional
        The logo of the app as a public http url, by default None
    scopes : List[str], optional
        The scopes, that this apps requires, will default to standard scopes, by default None
    url : str, optional
        The fakts_next server that will be used to configure this app, in a default ArkitektNext deployment this
        is the address of the "Lok Service" (which provides the Fakts API), by default DEFAULT_ARKITEKT_URL
        Will be overwritten by the FAKTS_URL environment variable
    headless : bool, optional
        Should we run in headless, mode, e.g printing necessary interaction into the console (will forexample
        stop opening browser windows), by default False
    log_level : str, optional
        The log-level to use, by default "ERROR"
    token : str, optional
        A fakts_next token to use, by default None
        Will be overwritten by the FAKTS_TOKEN environment variable
    no_cache : bool, optional
        Should we skip caching token, acess-token, by default False
        Attention: If this is set to True, the app will always have to be configured
        and authenticated.
    instance_id : str, optional
        The instance_id to use, by default "main"
        Can be set to a different value, if you want to run multiple intstances
        of the same app by the same user.
        Will be overwritten by the REKUEST_INSTANCE_ID environment variable
    register_reaktion : bool, optional
        Should we register the reaktion extension, by default True
        If set to False, the app will not be able to use the reaktion extension
        (which is necessary for scheduling in app` workflows from fluss)
    app_kind : str, optional
        The kind of app to create, by default "development"
        Can be set to "desktop" to create a desktop app, that can be used by multiple users.

    Returns
    -------
    NextApp
        A built app, that can be used to interact with the ArkitektNext server
    """
    registry = registry or get_default_service_registry()

    url = os.getenv("FAKTS_URL", url)
    token = os.getenv("FAKTS_TOKEN", token)

    manifest = Manifest(
        version=version,
        identifier=identifier,
        scopes=scopes if scopes else ["openid"],
        logo=logo,
        requirements=registry.get_requirements(),
        description=description,
    )
    if token:
        fakts_next = build_arkitekt_next_token_fakts_next(
            manifest=manifest,
            token=token,
            url=url,
        )

    elif redeem_token:
        fakts_next = build_arkitekt_next_redeem_fakts_next(
            manifest=manifest,
            redeem_token=redeem_token,
            url=url,
            no_cache=no_cache,
            headless=headless,
        )
    else:
        fakts_next = build_arkitekt_next_fakts_next(
            manifest=manifest,
            url=url,
            no_cache=no_cache,
            headless=headless,
            client_kind=app_kind,
        )

    herre_next = build_arkitekt_next_herre_next(fakts_next=fakts_next)

    params = kwargs

    create_arkitekt_next_folder(with_cache=True)

    try:
        from rich.logging import RichHandler

        logging.basicConfig(level=log_level, handlers=[RichHandler()])
    except ImportError:
        logging.basicConfig(level=log_level)

    app = QtApp(
        fakts=fakts_next,
        herre=herre_next,
        manifest=manifest,
        services=registry.build_service_map(
            fakts=fakts_next, herre=herre_next, params=params, manifest=manifest
        ),
    )

    app.enter()

    return app


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
) -> QtApp:
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

    fakts_next = build_arkitekt_next_qt_fakts_next(
        manifest=manifest,
        beacon_widget=beacon_widget,
        parent=parent,
        settings=settings,
    )

    herre_next = build_arkitekt_next_qt_herre_next(
        manifest,
        fakts=fakts_next,
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

    app = QtApp(
        fakts=fakts_next,
        herre=herre_next,
        manifest=manifest,
        services=registry.build_service_map(
            fakts=fakts_next, herre=herre_next, params=params, manifest=manifest
        ),
    )

    app.enter()

    return app
