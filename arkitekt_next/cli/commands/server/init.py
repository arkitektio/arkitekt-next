import rich_click as click
from click import Context
from blok.cli import create_cli
import asyncio
from typing import Optional
import os
from arkitekt_next.cli.vars import get_console
from arkitekt_next.__blok__ import get_bloks



bloks = get_bloks()

init = create_cli(*bloks)

