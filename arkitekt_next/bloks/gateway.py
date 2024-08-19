from arkitekt_next.bloks.services.name import NameService
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Any

from blok import blok, InitContext
from blok.bloks.services.dns import DnsService

DEFAULT_PUBLIC_URLS = ["127.0.0.1"]
DEFAULT_PUBLIC_HOSTS = ["localhost"]


class ExposedHost(BaseModel):
    host: str
    port: int
    stip_prefix: bool = True


class ExpostedToHost(BaseModel):
    port: int
    host: str
    to: str
    tls: bool = False


class ExposedPort(BaseModel):
    port: int
    host: str
    tls: bool = False
    to: int


@blok(
    "live.arkitekt.gateway", description="A gateway for exposing services on the host"
)
class GatewayBlok:
    def __init__(self) -> None:
        self.exposed_hosts = {}
        self.exposed_to_hosts = {}
        self.http_expose_default = None
        self.exposed_ports = {}
        self.with_certer = True
        self.with_tailscale = True
        self.certer_image = "jhnnsrs/certer:next"
        self.http_port = 80
        self.https_port = 443
        self.public_ips = DEFAULT_PUBLIC_URLS
        self.public_hosts = DEFAULT_PUBLIC_HOSTS

    def get_internal_host(self):
        return "caddy"

    def get_https_port(self):
        return 443

    def get_http_port(self):
        return 80

    def retrieve_gateway_network(self):
        return self.gateway_network

    def preflight(self, init: InitContext, dns: DnsService, name: NameService):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.public_ips = dns.get_dns_result().ip_addresses
        self.public_hosts = dns.get_dns_result().hostnames
        self.gateway_network = name.retrieve_name().replace("-", "_")

    def build(
        self,
        context: ExecutionContext,
    ):
        caddyfile = """
{
    auto_https off
}
        """

        for key, port in self.exposed_ports.items():
            if port.tls:
                caddyfile += f"""
:{port.port} {{
    tls /certs/caddy.crt /certs/caddy.key
    reverse_proxy {port.host}:{port.to}
}}
                """
            else:
                caddyfile += f"""
:{port.port} {{
    reverse_proxy {port.host}:{port.to}
}}
                """

        for protocol in ["http", "https"]:
            caddyfile += f"""
{protocol}:// {{
"""
            caddyfile += (
                """
    tls /certs/caddy.crt /certs/caddy.key
    """
                if protocol == "https"
                else ""
            )
            caddyfile += """
    header {
        -Server
        X-Forwarded-Proto {scheme}
        X-Forwarded-For {remote}
        X-Forwarded-Port {server_port}
        X-Forwarded-Host {host}
    }
        """

            for path_name, exposed_host in self.exposed_hosts.items():
                if exposed_host.stip_prefix:
                    caddyfile += f"""
    @{path_name} path /{path_name}* 
    handle @{path_name} {{
        uri strip_prefix /{path_name}
        reverse_proxy {exposed_host.host}:{exposed_host.port}
    }}
                """
                else:
                    caddyfile += f"""
    @{path_name} path /{path_name}*
    handle @{path_name} {{
        reverse_proxy {exposed_host.host}:{exposed_host.port}
    }}
                """

            for path_name, exposed_to_host in self.exposed_to_hosts.items():
                caddyfile += f"""
    @{path_name} path /{path_name}*
    handle @{path_name} {{
        rewrite * /{exposed_to_host.to}{{uri}}
        reverse_proxy {exposed_to_host.host}:{exposed_to_host.port}
    }}
                """

            if self.http_expose_default:
                caddyfile += f"""
    handle {{
        reverse_proxy {self.http_expose_default.host}:{self.http_expose_default.port}
    }}
            """

            caddyfile += """
}
        """

        context.file_tree.set_nested("configs", "Caddyfile", caddyfile)

        caddy_depends_on = []
        if self.with_certer:
            caddy_depends_on.append("certer")

        exposed_ports_strings = [
            f"{port.port}:{port.port}" for port in self.exposed_ports.values()
        ]

        caddy_container = {
            "image": "caddy:latest",
            "volumes": ["./configs/Caddyfile:/etc/caddy/Caddyfile", "./certs:/certs"],
            "ports": [
                f"{self.http_port}:80",
                f"{self.https_port}:443",
            ]
            + exposed_ports_strings,
            "depends_on": caddy_depends_on,
            "networks": [self.gateway_network, "default"],
        }

        context.docker_compose.set_nested("services", "caddy", caddy_container)

        context.file_tree.set_nested("certs", {})
        certer_container = {
            "image": self.certer_image,
            "volumes": ["./certs:/certs"],
            "environment": {
                "DOMAIN_NAMES": ",".join(self.public_hosts),
                "IP_ADDRESSED": ",".join(self.public_ips),
            },
        }

        context.docker_compose.set_nested("services", "certer", certer_container)
        context.docker_compose.set_nested(
            "networks",
            self.gateway_network,
            {"driver": "bridge", "name": self.gateway_network},
        )

    def expose(self, path_name: str, port: int, host: str, strip_prefix: bool = False):
        self.exposed_hosts[path_name] = ExposedHost(
            host=host, port=port, stip_prefix=strip_prefix
        )

    def expose_mapped(self, path_name: str, port: int, host: str, to: str):
        self.exposed_to_hosts[path_name] = ExpostedToHost(host=host, port=port, to=to)

    def expose_default(self, port: int, host: str):
        self.http_expose_default = ExposedHost(host=host, port=port, stip_prefix=False)

    def expose_port(self, port: int, host: str, tls: bool = False):
        self.exposed_ports[port] = ExposedPort(port=port, host=host, tls=tls, to=port)

    def expose_port_to(self, port: int, host: str, to_port: int, tls: bool = False):
        self.exposed_ports[port] = ExposedPort(
            port=port, host=host, tls=tls, to=to_port
        )

    def get_options(self):
        with_public_urls = Option(
            subcommand="public_url",
            help="Which public urls to use",
            type=str,
            multiple=True,
            default=DEFAULT_PUBLIC_URLS,
            show_default=True,
        )
        with_public_services = Option(
            subcommand="public_hosts",
            help="Which public hosts to use",
            type=str,
            multiple=True,
            default=DEFAULT_PUBLIC_HOSTS,
            show_default=True,
        )

        return [with_public_urls, with_public_services]
