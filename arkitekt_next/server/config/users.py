"""User, Organization, and Membership models.

This module contains models for users, organizations, memberships,
and roles within the Arkitekt platform.
"""

from pydantic import BaseModel, ConfigDict, Field

from .utils import generate_alpha_numeric_string, generate_name


class User(BaseModel):
    """User account for the Arkitekt server."""

    username: str = Field(
        default_factory=generate_name,
        description="Username for the user",
    )
    password: str = Field(
        default_factory=generate_alpha_numeric_string,
        description="Password for the user",
    )
    email: str | None = Field(
        default=None,
        description="Email for the user (optional)",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class Membership(BaseModel):
    """Membership linking a user to an organization with specific roles."""

    user: str = Field(
        description="Username of the user",
    )
    organization: str = Field(
        description="Identifier of the organization",
    )
    roles: list[str] = Field(
        default_factory=lambda: ["user"],
        description="Roles for this user in the organization",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class Role(BaseModel):
    """Role definition within an organization."""

    name: str = Field(
        description="Name of the role",
    )
    description: str | None = Field(
        default=None,
        description="Description of the role",
    )
    organization: str = Field(
        default="arkitektio",
        description="Organization that this role belongs to",
    )
    identifier: str = Field(
        default_factory=generate_name,
        description="Unique identifier for the role within the organization",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class Organization(BaseModel):
    """Organization within the Arkitekt platform."""

    name: str = Field(
        default_factory=generate_name,
        description="Name of the organization",
    )
    description: str | None = Field(
        default=None,
        description="Description of the organization",
    )
    identifier: str = Field(
        default_factory=generate_name,
        description="Unique identifier for the organization",
    )
    owner: str | None = Field(
        default=None,
        description="Username of the owner. The owner is added as admin automatically.",
    )
    auto_configure: bool = Field(
        default=True,
        description="Whether to auto-configure this organization",
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    @property
    def bot_name(self) -> str:
        """Get the bot name for the organization."""
        return f"{self.name}_bot"


class EmailConfig(BaseModel):
    """Email configuration for sending emails from the Arkitekt server."""

    host: str = Field(description="SMTP host for sending emails")
    port: int = Field(default=587, description="SMTP port for sending emails")
    username: str = Field(description="SMTP username for sending emails")
    password: str = Field(description="SMTP password for sending emails")
    email: str = Field(description="Email address to use as the sender")

    model_config = ConfigDict(
        extra="forbid",
    )


def create_default_organization() -> Organization:
    """Create a default organization for the Arkitekt server."""
    return Organization(
        name="arkitektio",
        identifier="arkitektio",
        description="Default organization for the Arkitekt server",
    )


def create_default_users() -> list[User]:
    """Create default users for the Arkitekt server."""
    return [
        User(
            username="demo",
            password="demo",
        )
    ]


def create_default_memberships() -> list[Membership]:
    """Create default memberships for the Arkitekt server."""
    return [
        Membership(
            user="demo",
            organization="arkitektio",
            roles=["admin"],
        )
    ]
