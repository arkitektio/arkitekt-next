from typing import Dict, Any, Protocol

from cv2 import HOUGH_STANDARD
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class LivekitCredentials:
    api_key: str
    api_secret: str
    host: str
    port: int
    dependency: str | None = None


@service("io.livekit.livekit")
class LivekitService(Protocol):
    def get_access(self) -> LivekitCredentials: ...
