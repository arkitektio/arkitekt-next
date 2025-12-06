import rich_click as click
from arkitekt_next.utils import create_arkitekt_next_folder
import os
import yaml
from .types import Flavour
from kabinet.api.schema import SelectorInput

@click.group()
def selector():
    """
    Manage selectors
    """
    pass

@selector.command(name="add")
@click.argument("flavour")
@click.option("--kind", "-k", help="The kind of selector", prompt=True)
@click.option("--api-version", "-av", help="The api version of the selector", default=None)
@click.option("--api-thing", "-at", help="The api thing of the selector", default=None)
@click.option("--one-api-version", "-oav", help="The one api version of the selector", default=None)
@click.option("--cuda-cores", "-cc", help="The cuda cores of the selector", default=None, type=int)
@click.option("--frequency", "-fr", help="The frequency of the selector", default=None, type=int)
@click.option("--memory", "-m", help="The memory of the selector", default=None, type=int)
def add_selector(flavour, kind, api_version, api_thing, one_api_version, cuda_cores, frequency, memory):
    """
    Add a new selector to a flavour
    """
    arkitekt_next_folder = create_arkitekt_next_folder()
    flavour_folder = os.path.join(arkitekt_next_folder, "flavours", flavour)
    config_file = os.path.join(flavour_folder, "config.yaml")

    if not os.path.exists(config_file):
        raise click.ClickException(f"Flavour {flavour} does not exist")

    with open(config_file, "r") as f:
        data = yaml.safe_load(f)
    
    fl = Flavour(**data)
    
    selector = SelectorInput(
        kind=kind,
        apiVersion=api_version,
        apiThing=api_thing,
        oneapiVersion=one_api_version,
        cudaCores=cuda_cores,
        frequency=frequency,
        memory=memory
    )
    
    fl.selectors.append(selector)
    
    with open(config_file, "w") as f:
        yaml.dump(fl.model_dump(), f)
    
    click.echo(f"Added selector {selector} to flavour {flavour}")
