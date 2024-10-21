def missing_install(name: str, error: Exception):
    def real_missing_install(*args, **kwargs):
        raise ImportError(
            f"Missing import: {name}. Please install the missing package. "
        ) from error

    return real_missing_install


try:
    from rekuest_next.register import register
    from rekuest_next.agents.hooks import background
    from rekuest_next.agents.hooks import startup
    from rekuest_next.agents.context import context
    from rekuest_next.state.state import state
    from rekuest_next.actors.reactive.api import progress, aprogress
    from rekuest_next.actors.reactive.api import log, alog
    from rekuest_next.register import test, benchmark
    from rekuest_next.structures.model import model
    from rekuest_next.define import define
except ImportError as e:
    raise e
    register = missing_install("rekuest_next", e)
    background = missing_install("rekuest_next", e)
    startup = missing_install("rekuest_next", e)
    context = missing_install("rekuest_next", e)
    state = missing_install("rekuest_next", e)
    progress = missing_install("rekuest_next", e)
    aprogress = missing_install("rekuest_next", e)
    log = missing_install("rekuest_next", e)
    alog = missing_install("rekuest_next", e)

from .builders import easy, interactive
from .apps.types import App

__all__ = [
    "App",
    "register",
    "easy",
    "interactive",
    "publicqt",
    "jupy",
    "log",
    "alog",
    "progress",
    "aprogress",
    "scheduler",
    "register_structure",
    "group",
    "useGuardian",
    "useInstanceID",
    "useUser",
    "next",
    "state",
    "context",
    "background",
    "startup",
    "register_next",
]
