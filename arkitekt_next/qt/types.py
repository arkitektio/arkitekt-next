from arkitekt_next.apps.types import App, Fakts, Herre, Manifest
from typing import List, Callable, Dict, Any


class QtApp(App):
    """An app that is built with the easy builder"""

    fakts: Fakts
    herre: Herre
    manifest: Manifest
    services: Dict[str, Any]
    hooks: Dict[str, List[Callable]] = {
        "on_start": [],
        "on_stop": [],
        "on_error": [],
        "on_message": [],
        "on_warning": [],
        "on_info": [],
        "on_debug": [],
        "on_enter": [],
    }

    def register_hook(self, hook_name: str, hook: Callable):
        """Register a hook"""
        self.hooks[hook_name].append(hook)

    def run(self):
        """Run the app"""
        self.services["rekuest"].run()

    async def __aenter__(self):
        await super().__aenter__()
        for service in self.services.values():
            await service.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        for service in self.services.values():
            await service.__aexit__(exc_type, exc_value, traceback)
