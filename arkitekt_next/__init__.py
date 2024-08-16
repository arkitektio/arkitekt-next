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
except ImportError as e:
    raise e
    register = missing_install("rekuest_next", e)
    background = missing_install("rekuest_next", e)
    startup = missing_install("rekuest_next", e)

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
    "background",
    "startup",
    "register_next",
]
