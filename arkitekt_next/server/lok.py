"""Programmatic control of a running Lok (coordination) server.

Lok is the one service every generated deployment includes (see
``dev.REQUIRED_SERVICES``) and the one a human normally drives through its web
UI: approving device codes, authorizing hub registrations, seeding
users. ``LokController`` exposes those actions to tests by executing Django
management commands -- and, where lok ships no dedicated command,
``manage.py shell`` snippets -- inside the lok container of a ``dokker``
deployment.

The controller is deliberately thin: every method boils down to "run this
command in the lok service", so anything not covered here can be scripted via
``manage`` / ``shell`` directly::

    server.lok.shell("from karakter.models import User; print(User.objects.count())")
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dokker import Deployment
    from dokker.log_watcher import LogRoll

#: How the lok image invokes Django's management entrypoint.
MANAGE = "uv run python manage.py"

#: Identity that the generated config seeds into every deployment (see the
#: default users/organizations written by the config generator) and the
#: hub lok auto-configures from the default kommunity partners.
DEMO_USER = "demo"
DEMO_ORG = "arkitektio"
LOCAL_HUB = "localhost"


# The web UI approves a hub registration by building a Hub from the staged
# manifest and attaching it to the device code; the challenge endpoint then
# answers "granted" with the hub token. This replicates exactly that,
# server-side.
_APPROVE_HUB = """
from django.contrib.auth import get_user_model
from fakts import models
from fakts.services.hubs import create_hub_from_manifest
from karakter.models import Organization

dc = models.HubDeviceCode.objects.get(code={code!r})
org = Organization.objects.get(slug={org!r})
dc.hub = create_hub_from_manifest(dc.manifest_as_model, org)
dc.user = get_user_model().objects.get(username={user!r})
dc.save()
print("approved:" + dc.hub.token)
"""

_DENY_HUB = """
from fakts import models

dc = models.HubDeviceCode.objects.get(code={code!r})
dc.denied = True
dc.save()
print("denied:" + dc.code)
"""

_PENDING_HUB_CODES = """
from fakts import models

for dc in models.HubDeviceCode.objects.filter(
    hub__isnull=True, denied=False
):
    print("pending:" + dc.code)
"""

_DENY_MESH = """
from fakts import models

dc = models.MeshDeviceCode.objects.get(code={code!r})
dc.denied = True
dc.save()
print("denied:" + dc.code)
"""

# A mesh join is authorized once a per-machine ionscale auth key is minted and
# linked as ``auth_key``; until then (and unless denied) it is pending.
_PENDING_MESH_CODES = """
from fakts import models

for dc in models.MeshDeviceCode.objects.filter(
    auth_key__isnull=True, denied=False
):
    print("pending:" + dc.code)
"""

_EXPIRE_DEVICE_CODE = """
import datetime
from django.utils import timezone
from fakts import models

dc = models.DeviceCode.objects.get(code={code!r})
dc.expires_at = timezone.now() - datetime.timedelta(seconds=1)
dc.save()
print("expired:" + dc.code)
"""

_DENY_DEVICE_CODE = """
from fakts import models

dc = models.DeviceCode.objects.get(code={code!r})
dc.denied = True
dc.save()
print("denied:" + dc.code)
"""


@dataclass
class LokController:
    """Drive a deployed lok server the way a human operator would.

    Wraps ``dokker``'s exec API (``deployment.run``/``arun``) for the lok
    service. Sync methods suit test bodies; the ``a``-prefixed variants suit
    async callbacks such as ``device_code_hook``.
    """

    deployment: "Deployment"
    service: str = "lok"

    # -- primitives ---------------------------------------------------------

    def manage(self, args: str, *, raise_on_error: bool = True) -> "LogRoll":
        """Run ``manage.py <args>`` inside the lok container (sync)."""
        return self.deployment.run(
            self.service, f"{MANAGE} {args}", raise_on_error=raise_on_error
        )

    async def amanage(self, args: str, *, raise_on_error: bool = True) -> "LogRoll":
        """Run ``manage.py <args>`` inside the lok container (async)."""
        return await self.deployment.arun(
            self.service, f"{MANAGE} {args}", raise_on_error=raise_on_error
        )

    def shell(self, code: str, *, raise_on_error: bool = True) -> "LogRoll":
        """Run a Python snippet via ``manage.py shell -c`` (sync).

        The escape hatch for anything lok has no management command for --
        full ORM and service-layer access.
        """
        return self.manage(f"shell -c {shlex.quote(code)}", raise_on_error=raise_on_error)

    async def ashell(self, code: str, *, raise_on_error: bool = True) -> "LogRoll":
        """Run a Python snippet via ``manage.py shell -c`` (async)."""
        return await self.amanage(
            f"shell -c {shlex.quote(code)}", raise_on_error=raise_on_error
        )

    # -- app device-code flow (fakts login) ----------------------------------

    def validate_device_code(
        self,
        code: str,
        *,
        user: str = DEMO_USER,
        org: str = DEMO_ORG,
        hub: str = LOCAL_HUB,
    ) -> "LogRoll":
        """Approve a pending app device code, as the web UI grant page would."""
        return self.manage(self._validate_args(code, user, org, hub))

    async def avalidate_device_code(
        self,
        code: str,
        *,
        user: str = DEMO_USER,
        org: str = DEMO_ORG,
        hub: str = LOCAL_HUB,
    ) -> "LogRoll":
        """Async :meth:`validate_device_code` -- drop-in ``device_code_hook`` body."""
        return await self.amanage(self._validate_args(code, user, org, hub))

    @staticmethod
    def _validate_args(code: str, user: str, org: str, hub: str) -> str:
        return (
            f"validatecode --code {shlex.quote(code)} --user {shlex.quote(user)} "
            f"--org {shlex.quote(org)} --hub {shlex.quote(hub)}"
        )

    def deny_device_code(self, code: str) -> "LogRoll":
        """Deny a pending app device code (the challenge answers ``denied``)."""
        return self.shell(_DENY_DEVICE_CODE.format(code=code))

    def expire_device_code(self, code: str) -> "LogRoll":
        """Expire a pending app device code (the challenge answers ``expired``)."""
        return self.shell(_EXPIRE_DEVICE_CODE.format(code=code))

    # -- hub registration flow (hub connect) ---------------------------------

    @staticmethod
    def _parse_pending(logs: "LogRoll") -> list[str]:
        return [
            line.split("pending:", 1)[1]
            for _, line in logs
            if "pending:" in line
        ]

    def pending_hub_codes(self) -> list[str]:
        """Codes of hub registrations awaiting authorization."""
        return self._parse_pending(self.shell(_PENDING_HUB_CODES))

    async def apending_hub_codes(self) -> list[str]:
        """Async :meth:`pending_hub_codes`."""
        return self._parse_pending(await self.ashell(_PENDING_HUB_CODES))

    def approve_hub(
        self, code: str, *, org: str = DEMO_ORG, user: str = DEMO_USER
    ) -> "LogRoll":
        """Authorize a pending hub registration for ``org``.

        This is what completes an ``arkitekt-next hub connect`` -- the challenge
        endpoint answers ``granted`` with the hub token afterwards.
        """
        return self.shell(_APPROVE_HUB.format(code=code, org=org, user=user))

    async def aapprove_hub(
        self, code: str, *, org: str = DEMO_ORG, user: str = DEMO_USER
    ) -> "LogRoll":
        """Async :meth:`approve_hub`."""
        return await self.ashell(_APPROVE_HUB.format(code=code, org=org, user=user))

    def deny_hub(self, code: str) -> "LogRoll":
        """Deny a pending hub registration."""
        return self.shell(_DENY_HUB.format(code=code))

    async def adeny_hub(self, code: str) -> "LogRoll":
        """Async :meth:`deny_hub`."""
        return await self.ashell(_DENY_HUB.format(code=code))

    # -- mesh device-code flow (mesh join) -----------------------------------

    def pending_mesh_codes(self) -> list[str]:
        """Codes of mesh join requests awaiting authorization."""
        return self._parse_pending(self.shell(_PENDING_MESH_CODES))

    async def apending_mesh_codes(self) -> list[str]:
        """Async :meth:`pending_mesh_codes`."""
        return self._parse_pending(await self.ashell(_PENDING_MESH_CODES))

    def deny_mesh(self, code: str) -> "LogRoll":
        """Deny a pending mesh join request (the challenge answers ``denied``)."""
        return self.shell(_DENY_MESH.format(code=code))

    async def adeny_mesh(self, code: str) -> "LogRoll":
        """Async :meth:`deny_mesh`."""
        return await self.ashell(_DENY_MESH.format(code=code))
