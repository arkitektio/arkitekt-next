# The Arkitekt Next CLI

The `arkitekt-next` command line interface is the main tool for developing,
packaging and deploying **Plugin Apps**. It scaffolds new projects, manages the
app manifest, generates typed API code, containerizes your app into flavours and
runs it locally for development.

This page is a reference for the available command groups. Every command and
sub-command also ships with `--help`, so you can always discover the exact flags
from the terminal:

```bash
arkitekt-next --help
arkitekt-next kabinet --help
arkitekt-next manifest version --help
```

Each `--help` output also links to the matching page in the hosted
documentation. Those links live as constants in
[`arkitekt_next/cli/docs.py`](../arkitekt_next/cli/docs.py) — change
`DOCS_BASE_URL` or a route there and every `--help` epilogue updates with it.

| Command group | Hosted docs |
| :--- | :--- |
| `init` | <https://arkitekt.live/docs/cli/init> |
| `run` | <https://arkitekt.live/docs/cli/run> |
| `manifest` | <https://arkitekt.live/docs/cli/manifest> |
| `kabinet` | <https://arkitekt.live/docs/cli/kabinet> |
| `gen` | <https://arkitekt.live/docs/cli/gen> |
| `inspect` | <https://arkitekt.live/docs/cli/inspect> |
| `call` | <https://arkitekt.live/docs/cli/call> |

## Global options

| Option | Description |
| :--- | :--- |
| `--work-dir`, `-w` | The working directory for the app. Defaults to the current directory. All commands read and write the `.arkitekt_next` folder relative to this directory, so you can operate on a project without `cd`-ing into it. |

```bash
# Operate on a project located elsewhere without changing directories
arkitekt-next --work-dir ./my-app manifest inspect
```

> **Note:** Every command except `init` expects an initialized app. They will
> create the `.arkitekt_next` folder if needed and load the manifest from the
> working directory.

---

## `init` — Scaffold a new app

Creates a new Arkitekt Next app in the working directory. It writes an
entrypoint file (default `app.py`) seeded from a template and a
`.arkitekt_next/manifest.yaml` describing the app.

```bash
# Interactive — prompts for identifier, author and entrypoint
arkitekt-next init

# Non-interactive — accept all defaults
arkitekt-next init --yes --package-manager pip

# Fully specified
arkitekt-next init myapp \
  --identifier com.example.myapp \
  --version 0.1.0 \
  --author "Jane Doe" \
  --entrypoint app \
  --scopes read --scopes write \
  --package-manager uv
```

Key options:

| Option | Description |
| :--- | :--- |
| `PATH` | Optional sub-directory to create the app in. Defaults to `.`. |
| `--identifier`, `-i` | Unique app identifier in [reverse domain notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) (e.g. `com.example.myapp`). |
| `--version`, `-v` | App version. Must follow [semver](https://semver.org/). Defaults to `0.0.1`. |
| `--author` | Shown to users of your app. Defaults to the current OS user. |
| `--entrypoint`, `-e` | Name of the Python entrypoint file (without `.py`). Defaults to `app`. |
| `--template`, `-t` | Starting template: `simple` or `filter`. |
| `--scopes`, `-s` | One or more requested scopes (`read`, `write`). Repeatable. |
| `--package-manager`, `-pm` | `pip` or `uv`. Defaults to `uv` if it is installed, otherwise `pip`. |
| `--with-extra` | Extras to install with `arkitekt-next` when using `uv`. Defaults to `all`. |
| `--yes`, `-y` | Accept all defaults without prompting. |
| `--overwrite-manifest`, `-om` | Overwrite an existing manifest. |
| `--overwrite-app`, `-oa` | Overwrite an existing entrypoint file. |

When `--package-manager uv` is chosen, `uv` must be installed; the CLI runs
`uv init` and `uv add arkitekt-next[all]` for you.

📖 <https://arkitekt.live/docs/cli/init>

---

## `run` — Run your app locally

Runs your app against a (local or remote) Arkitekt instance.

```bash
# Development mode with hot-reloading
arkitekt-next run dev

# Production mode (no reloading, scalable)
arkitekt-next run prod

# Connect to a specific instance, unattended
arkitekt-next run dev --url http://localhost:8000 --headless
```

| Sub-command | Description |
| :--- | :--- |
| `dev` | Runs the app with auto-reload on code changes. Best for iterating. |
| `prod` | Runs the app without reloading, as it would run inside a container. |

Common options (shared by `dev` and `prod`):

| Option | Description |
| :--- | :--- |
| `--url`, `-u` | The `fakts_next` URL of the Arkitekt instance to connect to. |
| `--builder`, `-b` | The builder used to assemble the app. Defaults to `arkitekt_next.builders.easy`. |
| `--token`, `-t` | A token for the `fakts_next` instance (skips interactive auth). |
| `--instance-id`, `-i` | The instance id to register the app under. |
| `--redeem-token`, `-r` | A redeem token used for unattended authentication. |
| `--headless`, `-h` | Run without opening a browser for authentication. |
| `--log-level`, `-l` | The log level (e.g. `INFO`, `DEBUG`). |

`run dev` additionally accepts `--no-cache`/`-nc` to skip the fakts cache and
`--deep` to watch the whole directory tree for changes.

📖 <https://arkitekt.live/docs/cli/run>

---

## `manifest` — Manage the app manifest

The manifest describes the app — its identifier, version, author and the
**scopes** (rights) it requests. It is used to authenticate the app with the
platform.

### `manifest inspect`

Prints the current manifest as a table.

```bash
arkitekt-next manifest inspect
```

### `manifest version`

Updates the app version, following [semver](https://semver.org/).

```bash
arkitekt-next manifest version set 1.2.3   # set an explicit version
arkitekt-next manifest version patch       # 1.2.3 -> 1.2.4
arkitekt-next manifest version minor       # 1.2.3 -> 1.3.0
arkitekt-next manifest version major       # 1.2.3 -> 2.0.0
arkitekt-next manifest version prerelease  # 1.2.3 -> 1.2.3-rc.1
arkitekt-next manifest version build       # 1.2.3 -> 1.2.3+build.1
```

| Sub-command | Effect |
| :--- | :--- |
| `set [VERSION]` | Sets an explicit version. Without an argument, prompts and suggests the next patch. |
| `patch` | Bumps the patch number — bugfixes and small changes. |
| `minor` | Bumps the minor number — new, backwards-compatible features. |
| `major` | Bumps the major number — breaking changes. |
| `prerelease` | Appends/bumps a prerelease segment (e.g. `-rc.1`). |
| `build` | Appends/bumps a build segment (e.g. `+build.1`). |

`set` without an argument prompts you, suggesting the next patch version.

### `manifest scopes`

Inspect and modify the scopes your app requests.

```bash
arkitekt-next manifest scopes list        # scopes this app requests
arkitekt-next manifest scopes available   # all scopes the platform offers
arkitekt-next manifest scopes add write   # request additional scopes
arkitekt-next manifest scopes remove write
```

Scopes are validated against the platform's known scopes (currently `read` and
`write`); passing an unknown scope fails the command.

📖 <https://arkitekt.live/docs/cli/manifest>

---

## `kabinet` — Containerize and deploy

`kabinet` builds your app into Docker containers and deploys it to an Arkitekt
instance. A single app can declare multiple **flavours** (build recipes) for
different hardware — see [Flavours](flavours.md).

```bash
# Scaffold a default (vanilla) flavour, plus a devcontainer
arkitekt-next kabinet init --flavour vanilla --devcontainer

# Add a GPU flavour
arkitekt-next kabinet flavour add --flavour gpu --description "CUDA enabled build"

# Attach a hardware selector to a flavour
arkitekt-next kabinet selector add gpu --kind cuda --cuda-cores 100

# Validate all flavour Dockerfiles and configs
arkitekt-next kabinet validate

# Build, stage and publish
arkitekt-next kabinet build
arkitekt-next kabinet stage
arkitekt-next kabinet publish
```

| Sub-command | Description |
| :--- | :--- |
| `init` | Scaffolds a flavour (Dockerfile + `config.yaml`) and optionally a devcontainer. |
| `flavour add` | Adds another build flavour to the project. |
| `selector add` | Adds a hardware selector (e.g. `cuda`) to a flavour. |
| `validate` | Validates every flavour's Dockerfile and `config.yaml`. |
| `build` | Builds the Docker image(s) for the selected flavour(s). |
| `stage` | Prepares a build for publishing. |
| `publish` | Publishes the built image(s) to a registry and registers them. |

`kabinet init` options:

| Option | Description |
| :--- | :--- |
| `--flavour`, `-f` | Name of the flavour to scaffold (e.g. `vanilla`, `gpu`). |
| `--template`, `-t` | Dockerfile template: `vanilla` or `uv`. |
| `--description`, `-d` | Human-readable description stored in the flavour's `config.yaml`. |
| `--arkitekt-version`, `-av` | The `arkitekt-next` version to pin in the generated Dockerfile. |
| `--devcontainer`, `-dc` | Also generate a `.devcontainer/<flavour>/devcontainer.json`. |
| `--overwrite`, `-o` | Overwrite an existing flavour of the same name. |

`kabinet build` options:

| Option | Description |
| :--- | :--- |
| `--flavour`, `-f` | The flavour to build. By default **all** flavours are built. |
| `--tag`, `-t` | Tag the resulting image with a specific tag. |
| `--no-inspect`, `-n` | Skip inspection of the app during the build. |
| `--url`, `-u` | The `fakts-next` server to use during inspection. |

`kabinet selector add <flavour>` attaches a hardware requirement to a flavour and
accepts `--kind`/`-k` (e.g. `cuda`) plus quantitative selectors such as
`--cuda-cores`/`-cc`, `--frequency`/`-fr` and `--memory`/`-m`. See
[Flavours](flavours.md) for how selectors drive deployment.

📖 <https://arkitekt.live/docs/cli/kabinet> · [Flavours guide](flavours.md)

---

## `gen` — Code generation

Generates fully typed Python code for your GraphQL API documents using
[turms](https://github.com/jhnnsrs/turms). Requires `turms` to be installed.

```bash
arkitekt-next gen init      # scaffold a graphql.config.yaml
arkitekt-next gen compile   # generate code once
arkitekt-next gen watch     # regenerate whenever documents change
```

`gen compile` accepts `--config` to point at a specific GraphQL config file
(defaults to the `graphql.config.yaml` created by `gen init`).

📖 <https://arkitekt.live/docs/cli/gen>

---

## `inspect` — Inspect your app

Inspects parts of your app. These commands are also used by the Arkitekt server
to introspect your app when it runs in production.

```bash
# Scan for module-level (leaking) variables that are unsafe on reload
arkitekt-next inspect variables

# Emit the app's requirements as JSON
arkitekt-next inspect requirements --pretty

# Emit the full agent manifest (implementations, states, requirements) as JSON
arkitekt-next inspect all --pretty
```

| Sub-command | Description |
| :--- | :--- |
| `variables` | Scans the entrypoint for dangerous global variables that can leak across reloads. |
| `requirements` | Prints the service requirements of the app as JSON. |
| `implementations` | Prints the registered implementations of the app. |
| `all` | Prints the complete agent manifest (implementations, states, locks, requirements, bloks). |

The JSON-emitting commands accept `--pretty`/`-p` for indented output and
`--machine-readable`/`-mr` for delimiter-wrapped output consumed by the server.

📖 <https://arkitekt.live/docs/cli/inspect>

---

## `call` — Call functions in your app

Calls functions defined in your app, either locally (no server needed) or
remotely (through a rekuest server).

```bash
arkitekt-next call remote <function> ...
```

📖 <https://arkitekt.live/docs/cli/call>

---

## Typical workflow

```bash
# 1. Create the app
arkitekt-next init myapp --identifier com.example.myapp --package-manager uv
cd myapp

# 2. Iterate locally
arkitekt-next run dev

# 3. Prepare for distribution
arkitekt-next kabinet init --flavour vanilla --devcontainer
arkitekt-next manifest version patch
arkitekt-next kabinet build
arkitekt-next kabinet publish
```
