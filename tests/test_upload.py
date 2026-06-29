from mikro_next.api.schema import create_dataset, from_array_like
import xarray as xr
import numpy as np
from .conftest import AppWithinDeployment
import pytest


@pytest.mark.integration
def test_create_dataset(running_app: AppWithinDeployment) -> None:
    """A dataset can be created against a running Arkitekt server."""
    dataset = create_dataset(name="Test Dataset")

    assert dataset is not None, "Dataset creation failed"
    assert dataset.id, "Created dataset has no id"
    assert dataset.name == "Test Dataset", "Dataset name was not persisted"


@pytest.mark.integration
def test_upload_into_dataset(running_app: AppWithinDeployment) -> None:
    """An array can be uploaded as an image into a freshly created dataset."""
    dataset = create_dataset(name="Upload Dataset")
    assert dataset.id, "Dataset creation failed"

    image = from_array_like(
        xr.DataArray(
            data=np.random.random((1000, 1000, 10)),
            dims=["x", "y", "z"],
        ),
        name="test_upload",
        dataset=dataset.id,
    )

    assert image.id, "Did not get an uploaded image back"
    assert image.data.shape == (
        1,
        1,
        10,
        1000,
        1000,
    ), "Did not write data according to schema ( T, C, Z, Y, X )"


@pytest.mark.integration
def test_write_random(running_app: AppWithinDeployment) -> None:
    """A random image can be written without an explicit dataset."""
    x = from_array_like(
        xr.DataArray(
            data=np.random.random((1000, 1000, 10)),
            dims=["x", "y", "z"],
        ),
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
