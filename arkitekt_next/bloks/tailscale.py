from pydantic import BaseModel
from typing import Dict, Any
from arkitekt_next.bloks.services.mount import MountService
from blok import blok, InitContext, Option, ExecutionContext
from arkitekt_next.bloks.services.gateway import GatewayService
from blok.bloks.services.dns import DnsService
from blok.tree import YamlFile


@blok("live.arkitekt.tailscale", description="Tailscale is a zero config VPN")
class TailscaleBlok:
    def __init__(self, name: str = "arkitekt") -> None:
        self.name = name
        self.disable = False

    def preflight(
        self,
        gateway: GatewayService,
        mount_service: MountService,
        dns: DnsService,
        net_name: str,
        auth_key: str,
        host_name: str,
        disable: bool = False,
    ):
        self.disable = disable
        if self.disable:
            return
        assert auth_key, "You need to provide an auth_key"

        self.caddy_service = gateway.get_internal_host()
        self.caddy_port = gateway.get_http_port()
        self.mount = mount_service.register_mount("tailscale_state", {})
        self.tailnet_name = net_name
        self.auth_key = auth_key
        self.dns_service = dns.get_dns_result()
        self.host_name = host_name

    def build(self, ex: ExecutionContext):
        if self.disable:
            return

        if not self.tailnet_name:
            # Trying to automatically find the hostname
            for i in self.dns_service.hostnames:
                if i.endswith(".ts.net"):
                    self.tailnet_name = i.split(".")[1]
                    break

        service = {
            "image": "jhnnsrs/tailproxy:latest",
            "volumes": [
                f"{self.mount}:/var/lib/tailscale"  # Persist the tailscale state directory
            ],
            "environment": [
                "TS_STATE_DIR=/var/lib/tailscale",
                f"TS_AUTH_KEY={self.auth_key}",
                f"TS_HOSTNAME={self.host_name}",
                f"TS_TAILNET={self.tailnet_name}",
                f"CADDY_TARGET={self.caddy_service}:{self.caddy_port}",
            ],
        }

        ex.docker_compose.set_nested("services", "tailscale_proxy", service)

    def get_options(self):
        return [
            Option(
                subcommand="net_name",
                help="The name of your tailnet",
                type=str,
            ),
            Option(
                subcommand="auth_key",
                help="The auth_key of your tailnet",
                type=str,
            ),
            Option(
                subcommand="host_name",
                help="The hostname of your tailnet",
                default=self.name,
                type=str,
            ),
            Option(
                subcommand="disable",
                help="Should we disable the creation of the tailscale service?",
                default=self.disable,
                type=str,
            ),
        ]
