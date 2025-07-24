from mikro_next.api.schema import create_dataset, from_array_like
import xarray as xr
import numpy as np
from .conftest import AppWithinDeployment
import pytest

@pytest.mark.integration
def test_upload(running_app: AppWithinDeployment) -> None:
    """Test the upload functionality of the app."""
    
    dataset = create_dataset(
        name="Test Dataset",
    )
    
    assert dataset is not None, "Dataset creation failed"
    
    
    
@pytest.mark.integration
def test_write_random(running_app: AppWithinDeployment) -> None:
    """Test writing a random image."""
    x = from_array_like(
        xr.DataArray(data=np.random.random((1000, 1000, 10)), dims=["x", "y", "z"]),
        name="test_random_write",
    )
    assert x.id, "Did not get a random rep"
    assert x.data.shape == (
        1,
        1,
        10,
        1000,
        1000,
    ), "Did not write data according to schema ( T, C, Z, Y, X )"
