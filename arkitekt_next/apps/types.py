"""
This module contains the types for the apps
depending on the builder used.

This module imports all the apps and their types
and sets them as attributes on the App class, if they are available.
If they are not available, they are set to Any, so that we can add
an import exception to the app.


"""

import logging
from typing import TYPE_CHECKING, Any, Dict
from arkitekt_next.base_models import Manifest
from koil.composition import Composition
from fakts_next import Fakts
from herre_next import Herre
from koil.helpers import KoilTask

logger = logging.getLogger(__name__)


class App(Composition):
    """An app that is built with the easy builder"""

    fakts: Fakts
    herre: Herre
    manifest: Manifest
    services: Dict[str, Any]

    def run(self):
        """Run the app"""
        return self.services["rekuest"].run()

    def run_detached(self) -> KoilTask:
        """Run the app detached"""

        return self.services["rekuest"].run_detached()

    def register(self, *args, **kwargs):
        """Register a service"""
        self.services["rekuest"].register(*args, **kwargs)

    async def __aenter__(self):
        await super().__aenter__()
        for service in self.services.values():
            await service.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        for service in self.services.values():
            await service.__aexit__(exc_type, exc_value, traceback)
