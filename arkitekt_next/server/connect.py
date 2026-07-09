"""Connect a hub to an organization.

A reusable, dependency-light module that:

1. Inspects the machine's current host addresses (via ``ifaddr``) and reverse-resolves
   their names.
2. Builds a ``HubStartRequest`` that advertises each enabled hub service as an
   instance, with one absolute alias per discovered host (pointing at the hub's
   gateway port + the service's path).
3. POSTs it to the organization's coordination (Lok) server, opens the browser so the
   operator can authorize the hub, and polls the challenge until it completes.

The models mirror the shapes the remote ``lok/f/hubstart/`` endpoint expects.
"""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import queue
import socket
import threading
import webbrowser
from typing import TYPE_CHECKING, Any, Callable

import ifaddr
from pydantic import BaseModel, Field

from arkitekt_next.node_id import get_or_set_node_id

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from arkitekt_next.server.config import HubConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hub models (match the remote lok hubstart schema)
# ---------------------------------------------------------------------------


class PublicSource(BaseModel):
    kind: str
    url: str


class Role(BaseModel):
    key: str
    description: str


class Scope(BaseModel):
    key: str
    description: str


class ServiceManifest(BaseModel):
    identifier: str
    name: str
    description: str
    version: str = "1.0.0"
    public_sources: list[PublicSource] = Field(default_factory=list)
    roles: list[Role] = Field(default_factory=list)
    scopes: list[Scope] = Field(default_factory=list)
    node_id: str | None = Field(default_factory=get_or_set_node_id)


class StagingAlias(BaseModel):
    id: str
    name: str
    host: str
    port: int
    path: str | None = None
    ssl: bool = False
    challenge: str | None = "ht"
    kind: str = "absolute"


class InstanceConfigure(BaseModel):
    manifest: ServiceManifest
    identifier: str | None = None
    aliases: list[StagingAlias]


class HubManifest(BaseModel):
    identifier: str | None = None
    instances: list[InstanceConfigure] = Field(default_factory=list)


class HubStartRequest(BaseModel):
    hub: HubManifest
    expiration_time_seconds: int = 600


# ---------------------------------------------------------------------------
# Host discovery
# ---------------------------------------------------------------------------


# Interface-name prefixes whose addresses live on virtual bridges / container /
# VM / VPN-internal networks. These are only reachable from *this* host (or its
# containers) and must never be advertised to the outside world. Matching is
# case-insensitive and prefix-based, which is how these interfaces are named
# across the common runtimes.
_VIRTUAL_IFACE_PREFIXES = (
    "docker",      # docker0
    "br-",         # docker user-defined bridge networks (br-<hash>)
    "veth",        # docker / lxc veth pairs
    "virbr",       # libvirt / KVM default bridge
    "vnet",        # libvirt guest taps
    "vmnet",       # VMware
    "vboxnet",     # VirtualBox host-only
    "cni",         # kubernetes CNI
    "cbr",         # kubernetes cbr0
    "flannel",     # kubernetes flannel
    "cali",        # kubernetes calico
    "kube",        # kubernetes misc
    "nerdctl",     # nerdctl bridges
    "podman",      # podman bridges
    "cni-podman",  # podman CNI bridges
)


def _is_virtual_interface(name: str) -> bool:
    """True if ``name`` looks like a Docker/VM/Kubernetes virtual interface."""
    lname = name.lower()
    return any(lname.startswith(prefix) for prefix in _VIRTUAL_IFACE_PREFIXES)


def _primary_outbound_ip() -> str | None:
    """Best-effort: the local IP the OS would use to reach the internet.

    Opens a *connected* UDP socket, which makes the kernel pick a source address
    from the routing table **without sending any packets**, then reads it back.
    This is the single most "outside-facing" address on the machine and is the
    one we want to advertise first. Returns ``None`` when it can't be determined
    (e.g. no default route / no network).
    """
    for probe, family in (
        ("8.8.8.8", socket.AF_INET),
        ("1.1.1.1", socket.AF_INET),
        ("2001:4860:4860::8888", socket.AF_INET6),
    ):
        try:
            with socket.socket(family, socket.SOCK_DGRAM) as sock:
                sock.settimeout(0)
                sock.connect((probe, 80))
                addr = sock.getsockname()[0]
        except OSError:
            continue
        if addr and not addr.startswith("0."):
            return addr
    return None


def _reverse_resolve(addr: str, timeout: float) -> tuple[str, list[str]] | None:
    """Reverse-resolve ``addr`` to ``(hostname, aliases)`` within ``timeout`` seconds.

    ``socket.gethostbyaddr`` is a blocking call that honours neither
    ``socket.setdefaulttimeout`` nor any argument, so a slow / black-holed PTR
    resolver would hang the discovery (and thus ``hub connect``) with no way to
    abort. We run it on a **daemon** thread and wait at most ``timeout`` for a
    result: daemon threads are abandoned at interpreter shutdown, so a still-blocked
    lookup can never keep the process alive (unlike a ``ThreadPoolExecutor`` worker,
    which ``concurrent.futures`` joins on exit). Returns ``None`` on timeout or
    failure -- callers treat that like an unresolved address.
    """
    result: "queue.Queue[tuple[str, list[str]] | None]" = queue.Queue(maxsize=1)

    def _worker() -> None:
        try:
            hostname, aliases, _ = socket.gethostbyaddr(addr)
            result.put((hostname, aliases))
        except OSError:
            result.put(None)

    thread = threading.Thread(target=_worker, name=f"ptr-{addr}", daemon=True)
    thread.start()
    try:
        return result.get(timeout=timeout)
    except queue.Empty:
        logger.debug("Reverse DNS for %s timed out after %.1fs", addr, timeout)
        return None


# Human-readable blurb per candidate kind, shown in the discovery table / prompt.
_KIND_LABELS = {
    "primary": "primary outbound route",
    "public": "public / globally routable",
    "private": "private LAN",
    "hostname": "reverse-DNS name",
}


class HostCandidate(BaseModel):
    """A single advertisable address, tagged with why it was discovered."""

    value: str
    #: one of ``primary`` / ``public`` / ``private`` / ``hostname``.
    kind: str
    #: source interface for IP candidates (``None`` for hostnames).
    interface: str | None = None
    #: for hostnames, the IP they were reverse-resolved from.
    resolved_from: str | None = None

    @property
    def is_ip(self) -> bool:
        return self.kind != "hostname"

    @property
    def description(self) -> str:
        base = _KIND_LABELS.get(self.kind, self.kind)
        if self.kind == "hostname" and self.resolved_from:
            return f"{base} of {self.resolved_from}"
        if self.interface:
            return f"{base} · {self.interface}"
        return base


def discover_host_candidates(
    *, resolve_names: bool = True, resolve_timeout: float = 2.0
) -> list[HostCandidate]:
    """Discover advertisable host addresses, classified and best route first.

    The goal is to advertise addresses at which *other* machines can reach this
    hub, so noise that only makes sense locally is dropped aggressively:

    * loopback (``127.0.0.0/8``) and link-local (``169.254.0.0/16``) addresses,
    * addresses bound to virtual bridges -- Docker (``docker0`` / ``br-*`` /
      ``veth*``), libvirt (``virbr*``), VMware, VirtualBox, Kubernetes CNIs --
      which are only reachable from this host and its containers (see
      :data:`_VIRTUAL_IFACE_PREFIXES`).

    Candidates are ordered so the most externally-reachable one leads: the
    primary outbound IP (the source address the OS would use to reach the
    internet) first, then any other globally-routable addresses, then
    private-LAN addresses. Reverse-DNS names, when ``resolve_names`` is set,
    follow the IP they resolve from. Each reverse lookup is bounded by
    ``resolve_timeout`` seconds (see :func:`_reverse_resolve`) so a slow resolver
    cannot stall discovery -- a lookup that overruns is treated as unresolved.
    """
    primary = _primary_outbound_ip()

    interface_of: dict[str, str] = {}
    for adapter in ifaddr.get_adapters():
        name = getattr(adapter, "name", "") or ""
        if isinstance(name, bytes):
            name = name.decode(errors="replace")
        if _is_virtual_interface(name):
            logger.debug("Skipping virtual interface %s", name)
            continue
        for ip in adapter.ips:
            addr = ip.ip
            # IPv6 addresses are (address, flowinfo, scope_id) tuples -- skip them.
            if not isinstance(addr, str):
                continue
            try:
                ip_obj = ipaddress.ip_address(addr)
            except ValueError:
                continue
            if ip_obj.is_loopback or ip_obj.is_link_local:
                continue
            interface_of.setdefault(addr, name)

    # 100.64.0.0/10 is CGNAT / shared address space (e.g. Tailscale). It is not
    # globally routable, so ``ipaddress.is_private`` (which excludes it) would
    # mislabel it as public -- treat it as private for classification/ranking.
    _shared = ipaddress.ip_network("100.64.0.0/10")

    def _is_private(addr: str) -> bool:
        ip_obj = ipaddress.ip_address(addr)
        return ip_obj.is_private or ip_obj in _shared

    def _rank(addr: str) -> tuple[int, str]:
        # Lower sorts first: primary outbound, then public, then private LAN.
        if addr == primary:
            return (0, addr)
        if not _is_private(addr):
            return (1, addr)
        return (2, addr)

    candidates: list[HostCandidate] = []
    seen: set[str] = set()
    for addr in sorted(interface_of, key=_rank):
        if addr == primary:
            kind = "primary"
        elif _is_private(addr):
            kind = "private"
        else:
            kind = "public"
        candidates.append(
            HostCandidate(value=addr, kind=kind, interface=interface_of[addr])
        )
        seen.add(addr)
        if resolve_names:
            resolved = _reverse_resolve(addr, resolve_timeout)
            if resolved is None:
                logger.debug("Could not resolve hostname for %s", addr)
                continue
            hostname, aliases = resolved
            for name in (hostname, *aliases):
                if name and name not in seen:
                    candidates.append(
                        HostCandidate(value=name, kind="hostname", resolved_from=addr)
                    )
                    seen.add(name)
    return candidates


def discover_hosts(
    *, resolve_names: bool = True, resolve_timeout: float = 2.0
) -> list[str]:
    """Return the machine's advertisable host addresses, best route first.

    Thin wrapper over :func:`discover_host_candidates` returning only the address
    strings. See that function for the discovery / filtering rules.
    """
    return [
        c.value
        for c in discover_host_candidates(
            resolve_names=resolve_names, resolve_timeout=resolve_timeout
        )
    ]


def build_aliases(
    hosts: list[str],
    *,
    port: int,
    ssl: bool,
    path: str | None = None,
    challenge: str = "ht",
) -> list[StagingAlias]:
    """Build one absolute alias per host for a service."""
    return [
        StagingAlias(
            id=host,
            name=host,
            host=host,
            port=port,
            path=path,
            challenge=challenge,
            ssl=ssl,
            kind="absolute",
        )
        for host in hosts
    ]


def build_hub(
    config: "HubConfig",
    hosts: list[str],
    *,
    identifier: str = "localhost",
) -> HubStartRequest:
    """Build the hub advertising every enabled hub service on ``hosts``."""
    from arkitekt_next.server.diff import iterate_services

    services = iterate_services(
        [
            config.rekuest,
            config.kabinet,
            config.mikro,
            config.fluss,
            config.elektro,
            config.alpaka,
            config.kraph,
        ]
    )

    use_ssl = config.gateway.ssl
    port = (
        config.gateway.exposed_https_port
        if use_ssl
        else config.gateway.exposed_http_port
    ) or (443 if use_ssl else 80)

    instances: list[InstanceConfigure] = []
    for svc in services:
        instances.append(
            InstanceConfigure(
                identifier=svc.get_name(),
                manifest=ServiceManifest(
                    identifier=f"live.arkitekt.{svc.get_identifier()}",
                    name=svc.get_name(),
                    description=svc.get_description(),
                    public_sources=[
                        PublicSource(kind="github", url=svc.github_repo)
                    ],
                    roles=[
                        Role(key=r.key, description=r.description)
                        for r in svc.get_roles()
                    ],
                    scopes=[
                        Scope(key=s.key, description=s.description)
                        for s in svc.get_scopes()
                    ],
                ),
                aliases=build_aliases(hosts, port=port, ssl=use_ssl, path=svc.host),
            )
        )

    return HubStartRequest(
        hub=HubManifest(identifier=identifier, instances=instances)
    )


# ---------------------------------------------------------------------------
# Registration flow
# ---------------------------------------------------------------------------


async def _post_json(session: "ClientSession", url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST ``payload`` as JSON to ``url`` and return the decoded JSON body."""
    async with session.post(
        url,
        json=payload,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    ) as response:
        # content_type=None: accept JSON even if the server does not set a
        # precise application/json content-type.
        return await response.json(content_type=None)


async def _hub_start(
    session: "ClientSession", base_url: str, request: HubStartRequest
) -> tuple[str | None, str | None, str]:
    """Start a hub registration; returns ``(code, challenge, configure_url)``.

    ``code`` identifies the request on the web authorization page; ``challenge``
    is the secret used to poll for the result.
    """
    data = await _post_json(session, f"{base_url}lok/f/hubstart/", request.model_dump())
    code = data.get("code")
    # Lok answers the start with ``challenge`` (the secret to poll with);
    # ``challenge_code`` is accepted for older servers.
    challenge = data.get("challenge") or data.get("challenge_code")
    configure_url = f"{base_url}hubconfigure/{code}"
    return code, challenge, configure_url


async def _hub_poll(
    session: "ClientSession",
    base_url: str,
    challenge: str,
    *,
    timeout: float,
    poll_interval: float,
    on_status: Callable[[str], None] | None,
) -> bool:
    """Poll the challenge endpoint until it is granted or ``timeout`` elapses."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        try:
            result = await _post_json(
                session, f"{base_url}lok/f/hubchallenge/", {"code": challenge}
            )
        except Exception as e:  # transient network error -- keep polling
            logger.debug("Challenge poll failed: %s", e)
            result = {}

        status = result.get("status")
        if on_status and status:
            on_status(status)
        # Lok reports an authorized hub as ``granted`` (with the hub token);
        # ``completed`` is accepted for older servers.
        if status in ("granted", "completed"):
            return True

        await asyncio.sleep(poll_interval)

    return False


async def register_hub(
    request: HubStartRequest,
    *,
    server: str,
    open_browser: bool = True,
    timeout: float = 120.0,
    poll_interval: float = 3.0,
    on_status: Callable[[str], None] | None = None,
) -> tuple[bool, str]:
    """Register ``request`` with the coordination server at ``server``.

    Returns ``(completed, configure_url)``. ``completed`` is True only if the
    challenge was granted before ``timeout``.

    ``server`` is a host name (``https://`` is assumed) or a full base URL with
    an explicit scheme (e.g. ``http://localhost:8010`` for a local deployment).
    """
    import aiohttp

    if "://" in server:
        base_url = f"{server.rstrip('/')}/"
    else:
        base_url = f"https://{server}/"

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        _code, challenge, configure_url = await _hub_start(session, base_url, request)

        if open_browser:
            # A wedged BROWSER handler can block; the printed link is the fallback.
            try:
                webbrowser.open(configure_url)
            except Exception:  # pragma: no cover - environment dependent
                pass

        if not challenge:
            return False, configure_url

        completed = await _hub_poll(
            session,
            base_url,
            challenge,
            timeout=timeout,
            poll_interval=poll_interval,
            on_status=on_status,
        )
        return completed, configure_url
