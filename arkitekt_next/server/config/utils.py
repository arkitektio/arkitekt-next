"""Utility functions for configuration generation."""

import secrets
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from pydantic import BaseModel, Field


def generate_django_secret_key() -> str:
    """Generate a 50-character Django SECRET_KEY."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for _ in range(50))


def generate_alpha_numeric_string(length: int = 40) -> str:
    """Generate a random alphanumeric string of a given length."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(chars) for _ in range(length))


# Word lists for the random name generator. Kept deliberately small, friendly and
# unambiguous so generated identifiers (usernames, org names, ...) read nicely.
_ADJECTIVES = (
    "ancient", "autumn", "billowing", "bold", "brave", "bright", "calm", "clever",
    "cool", "crimson", "curly", "damp", "dawn", "delicate", "divine", "dry", "empty",
    "falling", "floral", "fragrant", "frosty", "gentle", "green", "happy", "hidden",
    "holy", "icy", "jolly", "late", "lingering", "little", "lively", "long", "lucky",
    "misty", "morning", "muddy", "nameless", "noisy", "old", "patient", "polished",
    "proud", "purple", "quiet", "rapid", "restless", "rough", "shiny", "shy", "silent",
    "small", "snowy", "solitary", "sparkling", "spring", "still", "summer", "twilight",
    "wandering", "weathered", "wild", "winter", "wispy", "withered", "young",
)

_NOUNS = (
    "badger", "bird", "breeze", "brook", "bush", "butterfly", "cherry", "cloud",
    "darkness", "dawn", "dew", "dream", "dust", "feather", "field", "fire", "firefly",
    "flower", "fog", "forest", "frog", "frost", "glade", "glitter", "grass", "haze",
    "hill", "lake", "leaf", "lion", "log", "meadow", "moon", "morning", "mountain",
    "night", "otter", "owl", "paper", "pine", "pond", "rain", "resonance", "river",
    "sea", "shadow", "shape", "silence", "sky", "smoke", "snow", "snowflake", "sound",
    "star", "sun", "sunset", "surf", "thunder", "tree", "violet", "voice", "water",
    "waterfall", "wave", "wildflower", "wind", "wood",
)


def generate_name() -> str:
    """Generate a random, human-friendly ``adjective-noun`` name.

    Used as a default for usernames, organization names and similar identifiers.
    Produces lowercase, hyphen-separated names such as ``wandering-otter``.
    """
    return f"{secrets.choice(_ADJECTIVES)}-{secrets.choice(_NOUNS)}"


class KeyPair(BaseModel):
    """Asymmetric key pair for signing/verifying tokens."""

    key_type: str = Field(
        default="RSA256",
        description="Type of the key pair (e.g. RSA256, Ed25519)",
    )
    public_key: str = Field(..., description="Public key")
    private_key: str = Field(..., description="Private key")


def build_key_pair() -> KeyPair:
    """Generate a new RSA key pair (PEM private key, OpenSSH public key)."""
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=crypto_default_backend(),
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    ).decode()

    public_key = (
        key.public_key()
        .public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH,
        )
        .decode()
    )

    return KeyPair(public_key=public_key, private_key=private_key)


def build_ed25519_key_pair() -> KeyPair:
    """Generate a new Ed25519 key pair (PEM private + public keys).

    Used for the Rekuest provenance (attestation) signing key.
    """
    key = ed25519.Ed25519PrivateKey.generate()

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    ).decode()

    public_key = (
        key.public_key()
        .public_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    return KeyPair(key_type="Ed25519", public_key=public_key, private_key=private_key)
