"""Qt related modules.

This module contains Modules that are Qt related, and help to integrate
ArkitektNext with Qt applications.

The main component is the MagicBar, which is a widget that can be added
to any Qt application. It will then allow the user to configure and connect
to ArkitektNext, and configure settings.
"""

from .magic_bar import MagicBar
from .builders import publicqt, devqt
from .types import *

__all__ = ["MagicBar", "publicqt", "devqt", "QtApp"]
