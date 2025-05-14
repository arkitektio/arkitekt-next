from importlib import import_module
from typing import Callable
from arkitekt_next.apps.protocols import App


def import_builder(builder: str) -> Callable[..., App]:
    """ Import a builder function from a module.
    
    Parameters
    ----------
    builder : str
        The builder function to import, in the format "module.function".
        
    Returns
    -------
    Callable[..., App]
        The imported builder function.
    
    """
    
    module_path, function_name = builder.rsplit(".", 1)
    module = import_module(module_path)
    function = getattr(module, function_name)
    return function
