from typing import Dict, Any, List, Protocol, Optional
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class S3Credentials:
    name: str
    access_key: str
    buckets: Dict[str, str]
    host: str
    port: int
    secret_key: str
    protocol: str
    dependency: Optional[str] = None


@service("live.arkitekt.s3")
class S3Service(Protocol):
    def create_buckets(self, buckets: List[str]) -> S3Credentials: ...
