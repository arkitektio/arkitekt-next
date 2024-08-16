from .types import EasyApp
from typing import Optional, List


def build_arkitekt_app(
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

    try:
        from arkitekt_next_next.apps.service.rekuest_next import (
            build_arkitekt_next_rekuest_next,
        )

        rekuest = build_arkitekt_next_rekuest_next(
            fakts=fakts, herre=herre, instance_id=instance_id
        )
    except ImportError as e:
        rekuest = ImportException(import_exception=e, install_library="rekuest_next")

    try:
        from arkitekt_next_next.apps.service.mikro_next import (
            build_arkitekt_next_mikro_next,
        )

        mikro = build_arkitekt_next_mikro_next(fakts=fakts, herre=herre)
    except ImportError as e:
        raise e
        mikro = ImportException(import_exception=e, install_library="mikro_next")

    try:
        from arkitekt_next_next.apps.service.fluss_next import build_arkitekt_next_fluss

        fluss = build_arkitekt_next_fluss(herre=herre, fakts=fakts)
    except ImportError as e:
        raise e
        fluss = ImportException(import_exception=e, install_library="fluss_next")

    try:
        from arkitekt_next_next.apps.service.unlok_next import (
            build_arkitekt_next_unlok_next,
        )

        unlok = build_arkitekt_next_unlok_next(herre=herre, fakts=fakts)
    except ImportError as e:
        raise e
        fluss = ImportException(import_exception=e, install_library="fluss_next")

    try:
        from arkitekt_next_next.apps.service.omero_ark import (
            build_arkitekt_next_omero_ark,
        )

        omero_ark = build_arkitekt_next_omero_ark(herre=herre, fakts=fakts)
    except ImportError as e:
        omero_ark = ImportException(import_exception=e, install_library="omero_ark")

    try:
        from arkitekt_next_next.apps.service.kluster import build_arkitekt_next_kluster

        kluster = build_arkitekt_next_kluster(herre=herre, fakts=fakts)
    except ImportError as e:
        kluster = ImportException(import_exception=e, install_library="kluster")

    try:
        from arkitekt_next_next.apps.service.kabinet import build_arkitekt_next_kabinet

        kabinet = build_arkitekt_next_kabinet(herre=herre, fakts=fakts)
    except ImportError as e:
        kabinet = ImportException(import_exception=e, install_library="kluster")

    return NextApp(
        manifest=manifest,
        fakts=fakts,
        herre=herre,
        rekuest=rekuest,
        mikro=mikro,
        kabinet=kabinet,
        unlok=unlok,
        fluss=fluss,
        kluster=kluster,
        omero_ark=omero_ark,
    )
