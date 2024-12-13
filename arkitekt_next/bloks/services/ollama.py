from typing import Dict, Any, Protocol
from blok import blok, InitContext, Option
from blok import service
from dataclasses import dataclass


@dataclass
class OllamaCredentials:
    api_key: str
    api_secret: str
    api_url: str


@service("io.ollama.ollama", description=" A self-hosted ollama LLM server")
class OllamaService(Protocol):
    pass
