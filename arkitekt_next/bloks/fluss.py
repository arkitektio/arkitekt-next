import secrets
from arkitekt_next.bloks.funcs import (
    build_default_service_options,
    create_default_service_dependencies,
    create_default_service_yaml,
)
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


@blok("live.arkitekt.fluss")
class FlussBlok:
    def __init__(self) -> None:
        self.dev = False
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

    def get_builder(self):
        return "arkitekt.generic"

    def get_dependencies(self):
        return create_default_service_dependencies()

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        self.service = create_default_service_yaml(init, self)

        self.initialized = True

    def build(self, context: ExecutionContext):
        context.docker_compose.set_nested("services", self.host, self.service)

    def get_options(self):
        def_options = build_default_service_options(self)

        return [
            *def_options,
        ]
