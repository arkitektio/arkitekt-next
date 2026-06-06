# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`arkitekt-next` is a Python client SDK for the Arkitekt platform — a framework for hosting Python functions as remotely-callable, orchestratable nodes. Apps register Python functions via `@register`, connect to an Arkitekt server, and become available as building blocks in visual workflows. Requires Python ≥ 3.11.

## Commands

```bash
# Install all extras and dev dependencies
uv sync --all-extras --dev

# Run tests (exclude integration tests, which require a live Docker-based server)
uv run pytest -k "not integration"

# Run a single test file
uv run pytest tests/test_instantiation.py

# Run a single test by name
uv run pytest -k "test_easy"

# Run integration tests (spins up a local Arkitekt server via Docker)
uv run pytest -m integration

# Lint
uv run ruff check arkitekt_next/

# Build the package
uv build

# CLI (after install)
arkitekt-next --help
```

## Architecture

### App Lifecycle

The central abstraction is `App` (`arkitekt_next/app/app.py`), a subclass of `koil.composition.Composition` (an async context manager). Apps are built by calling either:

- `easy()` — standard development/plugin apps
- `interactive()` — Jupyter notebook apps (enters sync-in-async mode automatically)
- `qt()` — Qt desktop apps (returns `QtApp`, not `App`)

Both `easy()` and `qt()` follow the same build sequence in `builders.py`/`qt/builders.py`:
1. Create a `Manifest` (identifier, version, scopes, requirements from `ServiceBuilderRegistry`)
2. Pick an authentication flow based on available credentials
3. Build the service map via `ServiceBuilderRegistry.build_service_map()`
4. Run all registered `@init` hooks
5. Return the `App`

### Authentication (Fakts)

Three flows in `arkitekt_next/app/fakts.py`, selected by `easy()`:

| Condition | Flow | Use case |
|-----------|------|----------|
| `FAKTS_TOKEN` env / `token=` arg | `build_token_fakts` | Production/plugin deploys via kabinet |
| `redeem_token=` arg | `build_redeem_fakts` | Non-interactive app registration |
| Default | `build_device_code_fakts` | Interactive dev — opens browser for login |

All flows cache credentials to `.arkitekt_next/cache/<identifier>-<version>_fakts_cache.json`. Use `no_cache=True` or skip caching entirely with `FAKTS_TOKEN`.

Key env vars: `FAKTS_URL` (server URL), `FAKTS_TOKEN` (claim token), `REKUEST_INSTANCE_ID` (multi-instance), `ARKITEKT_NODE_ID` (override machine ID).

### Service Registry

`ServiceBuilderRegistry` (`arkitekt_next/service_registry.py`) is a global singleton that manages which platform services this app connects to. Services implement the `ArkitektService` protocol:

```python
class ArkitektService(Protocol):
    def get_service_name(self) -> str: ...
    def build_service(self, fakts: Fakts, params: Params) -> Optional[KoiledModel]: ...
    def get_requirements(self) -> list[Requirement]: ...
```

Optional services (mikro, fluss, unlok, alpaka, etc.) are registered by installing the corresponding optional extra (e.g. `pip install arkitekt-next[mikro]`). Use `require()` to declare an additional service dependency without building a full service.

### Init Hook Registry

`InitHookRegistry` (`arkitekt_next/init_registry.py`) holds callables of type `(App) -> None` that run at the end of `easy()`. Use the `@init` decorator to register hooks:

```python
from arkitekt_next import init

@init
def configure_logging(app: App):
    ...

@init(only_cli=True)
def cli_only_setup(app: App):
    ...  # only runs when invoked via arkitekt-next CLI
```

### Function Registration

Functions are registered with `@register` (from `rekuest_next`). Standard Python types are serialized automatically. Complex types need `shrink`/`expand` methods:

```python
class MyImage:
    id: str  # reference on remote storage

    async def shrink(self) -> str:
        return self.id

    @classmethod
    async def expand(cls, value: str) -> "MyImage":
        return cls.load_from_server(value)
```

### Node ID Persistence

`arkitekt_next/node_id.py` resolves a stable machine identifier in priority order:
1. `ARKITEKT_NODE_ID` environment variable
2. OS-level machine ID (`machineid.id()`)
3. UUID persisted in `platformdirs.user_config_dir("arkitekt_next", "arkitekt.live")/node_id.txt`

### CLI Architecture

Entry point: `arkitekt_next.cli.main:cli` (rich-click group). Context carries a `Console`, `Manifest`, and `work_dir` via `arkitekt_next/cli/vars.py`. Each command group lives in `arkitekt_next/cli/commands/<name>/`:

| Command | Purpose |
|---------|---------|
| `init` | Scaffold a new app (creates `app.py` from template + `.arkitekt_next/manifest.yaml`) |
| `run dev` | Hot-reload dev server — watches entrypoint; `--deep` watches all installed packages |
| `run prod` | Production runner |
| `gen compile/watch` | GraphQL codegen via turms (reads `.graphql` documents) |
| `kabinet build/publish/stage` | Docker image build and publish for deployment |
| `manifest` | Read/update `.arkitekt_next/manifest.yaml` |
| `inspect all/variables/requirements/implementations` | Introspect registered functions |
| `call` | Invoke a registered function remotely |

The manifest is stored as `.arkitekt_next/manifest.yaml`. The CLI's `Manifest` type (`arkitekt_next/cli/types.py`) is a Pydantic model distinct from `fakts_next.models.Manifest`.

App templates live in `arkitekt_next/cli/templates/` (currently `simple.py` and `filter.py`). GraphQL schemas for code generation live in `arkitekt_next/cli/schemas/`.

### Qt Integration

`from arkitekt_next.qt import qt, MagicBar`

`qt()` returns a `QtApp` (not `App`) with an embedded `MagicBar` widget for GUI-based login/configuration. Use as a drop-in for `easy()` in Qt applications.

## Testing

- Test markers: `integration` (requires live Docker Arkitekt stack), `qt` (requires Qt), `cli`
- The package registers as a pytest11 plugin providing `running_server` and `test_app` session-scoped fixtures for integration tests — these spin up a local Arkitekt server via `dokker` (Docker Compose wrapper)
- CLI tests use `click.testing.CliRunner` with isolated filesystem; see `tests/conftest.py` for `app_dir`, `app_runner`, and `initialized_app_cli_runner` fixtures
- CI runs on Python 3.11 and 3.12, Windows and Ubuntu, skipping integration tests

## Code Conventions

- **Linting**: ruff with `ANN` (type annotations) and `D1` (public docstrings required), line length 100
- All public functions/classes need docstrings with NumPy-style Parameters/Returns sections
- Optional dependencies (mikro, fluss, etc.) are guarded with try/except ImportError and replaced with `missing_install()` stub functions — see `__init__.py` pattern
- Async patterns are bridged to sync via `koil` (`unkoil()` for one-shot, `Koil(sync_in_async=True)` for notebooks)
- The `.arkitekt_next/` folder (created by `create_arkitekt_next_folder()`) is gitignored automatically for credentials/cache
