import secrets
from arkitekt_next.bloks.funcs import create_default_service_yaml
from blok import blok, InitContext, ExecutionContext, CLIOption
from blok.tree import YamlFile, Repo


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


@blok("live.arkitekt.fluss")
class FlussBlok:
    def __init__(self) -> None:
        self.host = "fluss"
        self.command = "bash run-debug.sh"
        self.image = "jhnnsrs/fluss:next"
        self.repo = "https://github.com/jhnnsrs/fluss-server-next"
        self.scopes = {"read_image": "Read image from the database"}
        self.mount_repo = False
        self.build_repo = False
        self.buckets = ["media"]
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos = []

    def get_dependencies(self):
        return [
            "live.arkitekt.mount",
            "live.arkitekt.config",
            "live.arkitekt.gateway",
            "live.arkitekt.postgres",
            "live.arkitekt.lok",
            "live.arkitekt.admin",
            "live.arkitekt.redis",
            "live.arkitekt.s3",
        ]

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.service = create_default_service_yaml(init, self)

        self.initialized = True

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        with_repo = CLIOption(
            subcommand="with_repo",
            help="Which repo should we use when building the service? Only active if build_repo or mount_repo is active",
            default=self.repo,
        )
        with_command = CLIOption(
            subcommand="command",
            help="Which command should be run when starting the service",
            default=self.command,
        )
        mount_repo = CLIOption(
            subcommand="mount_repo",
            help="Should we mount the repo into the container?",
            is_flag=True,
            default=self.mount_repo,
        )
        build_repo = CLIOption(
            subcommand="build_repo",
            help="Should we build the container from the repo?",
            is_flag=True,
            default=self.build_repo,
        )
        with_host = CLIOption(
            subcommand="host",
            help="How should the service be named inside the docker-compose file?",
            default=self.host,
        )
        with_secret_key = CLIOption(
            subcommand="secret_key",
            help="The secret key to use for the django service",
            default=self.secret_key,
        )

        return [
            with_repo,
            mount_repo,
            build_repo,
            with_host,
            with_command,
            with_secret_key,
        ]
