from arkitekt_next.bloks.services.certer import CerterService
from arkitekt_next.bloks.services.name import NameService
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Any, Optional

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


@blok("live.arkitekt.certer", description="A self-signed certificate generator")
class SelfSignedBlok:
    def __init__(self) -> None:
        self.host = "certer"
        self.certer_image = "jhnnsrs/certer:next"
        self.certs_mount = "./certs"

    def retrieve_certs_mount(self):
        return self.certs_mount

    def retrieve_depends_on(self):
        return ["certer"]

    def preflight(self, init: InitContext, dns: DnsService):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.public_ips = dns.get_dns_result().ip_addresses
        self.public_hosts = dns.get_dns_result().hostnames

    def build(
        self,
        context: ExecutionContext,
    ):

        context.file_tree.set_nested("certs", {})

        certer_container = {
            "image": self.certer_image,
            "volumes": ["./certs:/certs"],
            "environment": {
                "DOMAIN_NAMES": ",".join(self.public_hosts),
                "IP_ADDRESSED": ",".join(self.public_ips),
            },
        }

        context.docker_compose.set_nested("services", self.host, certer_container)

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
