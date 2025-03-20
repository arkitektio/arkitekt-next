"""Models for ArkitektNext. Thiese include extensiosn for the Fakts Manifest and the User model."""

from hashlib import sha256
import json
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional


class Requirement(BaseModel):
    key: str
    service: str
    """ The service is the service that will be used to fill the key, it will be used to find the correct instance. It needs to fullfill
    the reverse domain naming scheme"""
    optional: bool = False
    """ The optional flag indicates if the requirement is optional or not. Users should be able to use the client even if the requirement is not met. """
    description: Optional[str] = None
    """ The description is a human readable description of the requirement. Will be show to the user when asking for the requirement."""


class Manifest(BaseModel):
    """A manifest for an app that can be installed in ArkitektNext

    Manifests are used to describe apps that can be installed in ArkitektNext.
    They provide information about the app, such as the
    its globally unique identifier, the version, the scopes it needs, etc.

    This Manifest is send to the Fakts server on initial app configuration,
    and is used to register the app with the Fakts server, which in turn
    will prompt the user to grant the app access to establish itself as
    an ArkitektNext app (and therefore as an OAuth2 client) (see more in the
    Fakts documentation).

    """

    version: str
    """ The version of the app TODO: Should this be a semver? """
    identifier: str
    """ The globally unique identifier of the app: TODO: Should we check for a reverse domain name? """
    scopes: List[str]
    """ Scopes that this app should request from the user """
    logo: Optional[str]
    """ A URL to the logo of the app TODO: We should enforce this to be a http URL as local paths won't work """
    requirements: Optional[List[Requirement]] = Field(default_factory=list)
    """ Requirements that this app has TODO: What are the requirements? """
    model_config = ConfigDict(extra="forbid")
    
    description: Optional[str] = None
    """ A human readable description of the app """

    def hash(self):
        """Hash the manifest

        A manifest describes all the  metadata of an app. This method
        hashes the manifest to create a unique hash for the current configuration of the app.
        This hash can be used to check if the app has changed since the last time it was run,
        and can be used to invalidate caches.

        Returns:
            str: The hash of the manifest

        """

        unsorted_dict = self.model_dump()

        # sort the requirements
        unsorted_dict["requirements"] = sorted(
            unsorted_dict["requirements"], key=lambda x: x["key"]
        )
        # sort the scopes
        unsorted_dict["scopes"] = sorted(unsorted_dict["scopes"])

        # JSON encode the dictionary
        json_dd = json.dumps(unsorted_dict, sort_keys=True)
        # Hash the JSON encoded dictionary
        return sha256(json_dd.encode()).hexdigest()

    @field_validator("identifier")
    def check_identifier(cls, v):
        assert "/" not in v, "The identifier should not contain a /"
        assert len(v) > 0, "The identifier should not be empty"
        assert len(v) < 256, "The identifier should not be longer than 256 characters"
        return v


class User(BaseModel):
    """A user of ArkitektNext

    This model represents a user on ArkitektNext. As herre_next is acgnostic to the
    user model, we need to provide a model that can be used to represent
    the ArkitektNext user. This model is used by the
    :class:`herre_next.fakts.fakts_endpoint_fetcher.FaktsUserFetcher` to
    fetch the user from the associated ArkitektNext Lok instance. This model
    is closely mimicking the OIDC user model, and is therefore compatible
    to represent OIDC users.

    """

    id: str = Field(alias="sub")
    """ The user's id (in lok, this is the user's sub(ject) ID)"""

    username: str = Field(alias="preferred_username")
    """ The user's preferred username """
    email: str = Field(alias="email")
    """ The user's preferred username """
