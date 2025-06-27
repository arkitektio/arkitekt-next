from typing import Dict, Any, Optional, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class OllamaAccess:
    api_key: str
    api_secret: str
    api_url: str
    dependency: Optional[str] = None


@service("io.ollama.ollama", description=" A self-hosted ollama LLM server")
class OllamaService(Protocol):
    pass

    def get_access(self) -> OllamaAccess:
        """Get the credentials for the ollama service."""
        ...
