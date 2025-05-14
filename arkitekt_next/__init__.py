from .builders import easy, interactive
from .apps.protocols import App
from fakts_next.helpers import afakt, fakt
from .init_registry import init, InitHookRegistry, get_default_init_hook_registry
from .service_registry import (
    require,
    ServiceBuilderRegistry,
    get_default_service_registry,
)


def missing_install(name: str, error: Exception):
    def real_missing_install(*args, **kwargs):
        raise ImportError(
            f"Missing import: {name}. Please install the missing package. "
        ) from error

    return real_missing_install


try:
    from rekuest_next.register import register
    from rekuest_next.agents.hooks.background import background
    from rekuest_next.agents.hooks.startup import startup
    from rekuest_next.agents.context import context
    from rekuest_next.state.decorator import state
    from rekuest_next.actors.context import abreakpoint, breakpoint
    from rekuest_next.actors.context import progress, aprogress
    from rekuest_next.actors.context import log, alog
    from rekuest_next.structures.model import model
    from rekuest_next.actors.context import apublish, publish
    from rekuest_next.remote import (
        call,
        acall,
        acall_raw,
        iterate,
        aiterate,
        aiterate_raw,
        find,
    )
except ImportError as e:
    raise e
    publish = missing_install("rekuest_next", e)
    apublish = missing_install("rekuest_next", e)
    structure = missing_install("rekuest_next", e)
    register = missing_install("rekuest_next", e)
    background = missing_install("rekuest_next", e)
    abreakpoint = missing_install("rekuest_next", e)
    breakpoint = missing_install("rekuest_next", e)
    startup = missing_install("rekuest_next", e)
    context = missing_install("rekuest_next", e)
    find = missing_install("rekuest_next", e)
    state = missing_install("rekuest_next", e)
    progress = missing_install("rekuest_next", e)
    aprogress = missing_install("rekuest_next", e)
    log = missing_install("rekuest_next", e)
    alog = missing_install("rekuest_next", e)
    call = missing_install("rekuest_next", e)
    call_raw = missing_install("rekuest_next", e)
    acall = missing_install("rekuest_next", e)
    acall_raw = missing_install("rekuest_next", e)
    find = missing_install("rekuest_next", e)
    afind = missing_install("rekuest_next", e)
    aiterate_raw = missing_install("rekuest_next", e)
    aiterate = missing_install("rekuest_next", e)
    iterate = missing_install("rekuest_next", e)


__all__ = [
    "App",
    "require",
    "easy",
    "interactive",
    "log",
    "alog",
    "afakt",
    "fakt",
    "progress",
    "InitHookRegistry",
    "get_default_init_hook_registry",
    "aprogress",
    "ServiceBuilderRegistry",
    "get_default_service_registry",
    "register",
    "find",
    "breakpoint",
    "abreakpoint",
    "aiterate",
    "iterate",
    "aiterate_raw",
    "call",
    "acall",
    "acall_raw",
    "model",
    "state",
    "context",
    "background",
    "startup",
    "init",
    "InitHookRegisty",
    "get_current_init_hook_registry",
]
