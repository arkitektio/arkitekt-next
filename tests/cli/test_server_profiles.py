"""Tests for the hub / coord / hubinator / engine deployment profiles.

Covers the three deep, standalone schemas + their dedicated generators, the CLI
``init``/``up`` flows (per-profile config files), and the ``hub connect`` flow.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml
from click.testing import CliRunner

from arkitekt_next.cli.main import cli
from arkitekt_next.server.config import (
    ArkitektServerConfig,
    CoordConfig,
    EngineConfig,
    HubConfig,
)
from arkitekt_next.server.diff import (
    write_coord_files,
    write_engine_files,
    write_hub_files,
    write_virtual_config_files,
)


def _gen(fn, cfg):
    d = Path(tempfile.mkdtemp())
    fn(d, cfg)
    return d


def _configs(d: Path):
    cdir = d / "configs"
    return sorted(os.listdir(cdir)) if cdir.exists() else []


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


def test_hub_schema_has_no_identity_fields():
    h = HubConfig()
    for field in ("lok", "organizations", "users", "memberships", "deployer"):
        assert not hasattr(h, field), f"HubConfig should not carry {field}"
    assert h.coord_server == "go.arkitekt.live"
    assert hasattr(h, "rekuest")


def test_coord_schema_has_identity_but_no_data_services():
    c = CoordConfig()
    assert hasattr(c, "lok")
    assert c.organizations  # default org present
    for field in ("rekuest", "mikro", "fluss", "deployer"):
        assert not hasattr(c, field), f"CoordConfig should not carry {field}"


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def test_hubinator_generator_wires_local_lok():
    d = _gen(write_virtual_config_files, ArkitektServerConfig())
    assert (d / "configs" / "lok.yaml").exists()
    caddy = (d / "configs" / "Caddyfile").read_text()
    assert "/.well-known/*" in caddy
    rk = yaml.safe_load((d / "configs" / "rekuest.yaml").read_text())
    # Services trust the LOCAL lok JWKS.
    assert "lok" in rk["authentikate"]["issuers"][0]["jwks_uri"]


def test_hub_generator_delegates_auth_and_omits_lok():
    d = _gen(write_hub_files, HubConfig(coord_server="auth.example.org"))
    assert not (d / "configs" / "lok.yaml").exists()
    caddy = (d / "configs" / "Caddyfile").read_text()
    assert "/.well-known/*" not in caddy
    rk = yaml.safe_load((d / "configs" / "rekuest.yaml").read_text())
    # Services trust the REMOTE coordination server's JWKS.
    assert rk["authentikate"]["issuers"][0]["jwks_uri"] == (
        "https://auth.example.org/.well-known/jwks.json"
    )


def test_coord_generator_is_lok_only():
    d = _gen(write_coord_files, CoordConfig())
    comp = yaml.safe_load((d / "docker-compose.yaml").read_text())
    assert set(comp["services"]) == {"db", "redis", "minio", "minio_init", "lok", "gateway"}
    lok = yaml.safe_load((d / "configs" / "lok.yaml").read_text())
    assert lok["organizations"]  # provisions identities
    # No data-service config files.
    assert _configs(d) == ["Caddyfile", "lok.yaml", "minio_init.yaml"]


def test_engine_generator_is_deployer_only():
    d = _gen(write_engine_files, EngineConfig(url="https://go.example.org", network="netx"))
    comp = yaml.safe_load((d / "docker-compose.yaml").read_text())
    assert list(comp["services"]) == ["deployer"]
    assert comp["networks"]["netx"] == {"external": True}
    dep = comp["services"]["deployer"]
    assert "https://go.example.org" in dep["command"]
    assert dep["environment"]["ARKITEKT_NETWORK"] == "netx"


# ---------------------------------------------------------------------------
# CLI init / up
# ---------------------------------------------------------------------------


def test_hub_init_writes_config_without_identities():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        result = runner.invoke(
            cli,
            ["--work-dir", d, "hub", "init", "--template", "stable",
             "--coord-server", "auth.example.org", "--service", "rekuest"],
        )
        assert result.exit_code == 0, result.output
        data = yaml.safe_load(open(os.path.join(d, "hub_config.yaml")))
        assert data["kind"] == "hub"
        assert "lok" not in data["config"]
        assert "organizations" not in data["config"]
        assert data["config"]["coord_server"] == "auth.example.org"


def test_coord_init_template_skips_org_prompts():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        result = runner.invoke(cli, ["--work-dir", d, "coord", "init", "--template", "default"])
        assert result.exit_code == 0, result.output
        data = yaml.safe_load(open(os.path.join(d, "coord_config.yaml")))
        assert data["kind"] == "coord"
        assert data["config"]["organizations"]  # default org
        assert "mikro" not in data["config"]  # no data services


def test_coord_init_wizard_can_add_organizations():
    """With no template, the wizard asks about organizations."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        # Answers: admin user/pass/email, "Set up organizations? no", email? no
        # We patch the org-setup confirm to False to keep the flow deterministic.
        with patch("arkitekt_next.server.wizard.configure_global_admin",
                   return_value=("admin", "pw", None)), \
             patch("arkitekt_next.server.wizard.configure_email", return_value=None), \
             patch("click.confirm", return_value=False):
            result = runner.invoke(cli, ["--work-dir", d, "coord", "init"])
        assert result.exit_code == 0, result.output
        data = yaml.safe_load(open(os.path.join(d, "coord_config.yaml")))
        assert data["kind"] == "coord"


def test_hubinator_init_writes_its_own_file():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        result = runner.invoke(cli, ["--work-dir", d, "hubinator", "init", "--template", "default"])
        assert result.exit_code == 0, result.output
        assert os.path.exists(os.path.join(d, "hubinator_config.yaml"))


def test_engine_init_and_up():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(
            cli,
            ["--work-dir", d, "engine", "init", "--url", "https://go.x",
             "--redeem-token", "tok", "--network", "netx"],
        )
        data = yaml.safe_load(open(os.path.join(d, "engine_config.yaml")))
        assert data["kind"] == "engine"
        assert data["config"]["deployer"]["redeem_token"] == "tok"

        with patch("arkitekt_next.server.runner.compose_up") as cu, \
             patch("shutil.which", return_value="/usr/bin/docker"):
            result = runner.invoke(cli, ["--work-dir", d, "engine", "up"])
        assert result.exit_code == 0, result.output
        assert cu.called
        comp = yaml.safe_load(open(os.path.join(d, "docker-compose.yaml")))
        assert list(comp["services"]) == ["deployer"]


def test_coord_up_roundtrips_and_generates_lok_only():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(cli, ["--work-dir", d, "coord", "init", "--template", "default"])
        with patch("arkitekt_next.server.runner.compose_up") as cu, \
             patch("shutil.which", return_value="/usr/bin/docker"):
            result = runner.invoke(cli, ["--work-dir", d, "coord", "up"])
        assert result.exit_code == 0, result.output
        assert cu.called
        assert os.path.exists(os.path.join(d, "configs", "lok.yaml"))
        assert not os.path.exists(os.path.join(d, "configs", "rekuest.yaml"))


def test_hubinator_up_roundtrips_full_stack():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(cli, ["--work-dir", d, "hubinator", "init", "--template", "default"])
        with patch("arkitekt_next.server.runner.compose_up") as cu, \
             patch("shutil.which", return_value="/usr/bin/docker"):
            result = runner.invoke(cli, ["--work-dir", d, "hubinator", "up"])
        assert result.exit_code == 0, result.output
        assert cu.called
        # Full stack: local lok + data services.
        assert os.path.exists(os.path.join(d, "configs", "lok.yaml"))
        assert os.path.exists(os.path.join(d, "configs", "rekuest.yaml"))


def test_hub_up_generates_and_runs():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(cli, ["--work-dir", d, "hub", "init", "--template", "stable", "--service", "rekuest"])
        with patch("arkitekt_next.server.runner.compose_up") as cu, \
             patch("shutil.which", return_value="/usr/bin/docker"):
            result = runner.invoke(cli, ["--work-dir", d, "hub", "up"])
        assert result.exit_code == 0, result.output
        assert cu.called
        assert os.path.exists(os.path.join(d, "docker-compose.yaml"))
        assert not os.path.exists(os.path.join(d, "configs", "lok.yaml"))


# ---------------------------------------------------------------------------
# hub connect
# ---------------------------------------------------------------------------


class _FakeIP:
    def __init__(self, ip):
        self.ip = ip


class _FakeAdapter:
    def __init__(self, ips, name=""):
        self.name = name
        self.ips = [_FakeIP(i) for i in ips]


def test_hub_connect_advertises_services_and_filters_local_ips():
    runner = CliRunner()
    posts = []

    async def fake_post(session, url, payload):
        posts.append((url, payload))
        # Shapes mirror the real lok server: the start answers with ``challenge``
        # and an authorized challenge polls as ``granted`` (with the token).
        if "hubstart" in url:
            return {"status": "granted", "code": "CODE123", "challenge": "CH"}
        return {"status": "granted", "token": "TOK"}

    adapters = [
        _FakeAdapter(["192.168.1.50"], name="eth0"),
        _FakeAdapter(["127.0.0.1"], name="lo"),          # loopback -> filtered
        _FakeAdapter(["169.254.0.9"], name="eth0"),      # link-local -> filtered
        _FakeAdapter([("fe80::1", 0, 0)], name="eth0"),  # IPv6 tuple -> skipped
        _FakeAdapter(["172.17.0.1"], name="docker0"),    # docker bridge -> filtered
        _FakeAdapter(["172.20.0.1"], name="br-a1b2c3"),  # docker network -> filtered
        _FakeAdapter(["192.168.122.1"], name="virbr0"),  # libvirt bridge -> filtered
    ]

    with tempfile.TemporaryDirectory() as d:
        runner.invoke(
            cli,
            ["--work-dir", d, "hub", "init", "--template", "stable",
             "--service", "rekuest", "--service", "mikro", "--coord-server", "go.arkitekt.live"],
        )
        with patch("ifaddr.get_adapters", return_value=adapters), \
             patch("socket.gethostbyaddr", side_effect=OSError), \
             patch("arkitekt_next.server.connect._post_json", side_effect=fake_post), \
             patch("webbrowser.open") as wb:
            result = runner.invoke(cli, ["--work-dir", d, "hub", "connect", "--timeout", "1"])

    assert result.exit_code == 0, result.output
    start = next(p for p in posts if "hubstart" in p[0])
    instances = start[1]["hub"]["instances"]
    assert sorted(i["manifest"]["identifier"] for i in instances) == [
        "live.arkitekt.mikro",
        "live.arkitekt.rekuest",
    ]
    # Only the routable IP is advertised.
    assert sorted(a["host"] for a in instances[0]["aliases"]) == ["192.168.1.50"]
    assert wb.call_args[0][0] == "https://go.arkitekt.live/hubconfigure/CODE123"
    assert "connected to the organization" in result.output


def test_discover_host_candidates_classifies_and_filters():
    from arkitekt_next.server.connect import discover_host_candidates

    adapters = [
        _FakeAdapter(["203.0.113.5"], name="eth0"),      # public
        _FakeAdapter(["192.168.1.50"], name="eth0"),     # private LAN
        _FakeAdapter(["100.100.1.2"], name="tailscale0"),  # CGNAT -> private
        _FakeAdapter(["127.0.0.1"], name="lo"),          # loopback -> filtered
        _FakeAdapter(["172.17.0.1"], name="docker0"),    # docker -> filtered
        _FakeAdapter(["172.20.0.1"], name="br-abc"),     # docker net -> filtered
        _FakeAdapter(["192.168.122.1"], name="virbr0"),  # libvirt -> filtered
    ]

    def fake_resolve(addr):
        if addr == "203.0.113.5":
            return ("host.example.org", [], [addr])
        raise OSError

    with patch("ifaddr.get_adapters", return_value=adapters), \
         patch("socket.gethostbyaddr", side_effect=fake_resolve), \
         patch("arkitekt_next.server.connect._primary_outbound_ip", return_value="203.0.113.5"):
        cands = discover_host_candidates(resolve_names=True)

    by_value = {c.value: c for c in cands}
    # Virtual bridges / loopback dropped entirely.
    assert set(by_value) == {"203.0.113.5", "host.example.org", "192.168.1.50", "100.100.1.2"}
    # Primary outbound leads, is classified as such, and carries its interface.
    assert cands[0].value == "203.0.113.5"
    assert by_value["203.0.113.5"].kind == "primary"
    assert by_value["203.0.113.5"].interface == "eth0"
    # CGNAT (Tailscale) is treated as private, not public.
    assert by_value["100.100.1.2"].kind == "private"
    assert by_value["192.168.1.50"].kind == "private"
    # The reverse-DNS name is a separate, hostname-kind candidate.
    assert by_value["host.example.org"].kind == "hostname"
    assert by_value["host.example.org"].resolved_from == "203.0.113.5"
    assert by_value["host.example.org"].is_ip is False


def test_discover_host_candidates_can_skip_name_resolution():
    from arkitekt_next.server.connect import discover_host_candidates

    adapters = [_FakeAdapter(["192.168.1.50"], name="eth0")]
    with patch("ifaddr.get_adapters", return_value=adapters), \
         patch("socket.gethostbyaddr") as resolve, \
         patch("arkitekt_next.server.connect._primary_outbound_ip", return_value=None):
        cands = discover_host_candidates(resolve_names=False)

    assert [c.value for c in cands] == ["192.168.1.50"]
    resolve.assert_not_called()


def test_discover_host_candidates_bounds_slow_reverse_dns():
    """A hanging PTR lookup must not stall discovery -- the bound drops the name."""
    import time

    from arkitekt_next.server.connect import discover_host_candidates

    adapters = [_FakeAdapter(["203.0.113.5"], name="eth0")]

    def slow_resolve(addr):
        time.sleep(5)  # would hang discovery without the resolve_timeout bound
        return ("slow.example.org", [], [addr])

    with patch("ifaddr.get_adapters", return_value=adapters), \
         patch("socket.gethostbyaddr", side_effect=slow_resolve), \
         patch("arkitekt_next.server.connect._primary_outbound_ip", return_value=None):
        start = time.monotonic()
        cands = discover_host_candidates(resolve_names=True, resolve_timeout=0.2)
        elapsed = time.monotonic() - start

    # Returned promptly (did not wait for the 5s lookup) ...
    assert elapsed < 2.0
    # ... and dropped the unresolved name, keeping the routable IP.
    assert [c.value for c in cands] == ["203.0.113.5"]


def test_hub_connect_threads_resolve_timeout():
    """`hub connect --resolve-timeout` reaches ``discover_host_candidates``."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(
            cli,
            ["--work-dir", d, "hub", "init", "--template", "stable",
             "--service", "rekuest", "--coord-server", "go.arkitekt.live"],
        )
        with patch(
            "arkitekt_next.server.connect.discover_host_candidates", return_value=[]
        ) as disc:
            result = runner.invoke(
                cli,
                ["--work-dir", d, "hub", "connect", "--resolve-timeout", "0.5", "--all-hosts"],
            )

    # Empty discovery aborts cleanly, but the option was threaded through.
    assert result.exit_code != 0
    assert disc.call_args.kwargs.get("resolve_timeout") == 0.5
