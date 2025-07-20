from mikro_next.api.schema import create_dataset
from .conftest import AppWithinDeployment
import pytest

@pytest.mark.integration
def test_upload(running_app: AppWithinDeployment) -> None:
    """Test the upload functionality of the app."""
    
    dataset = create_dataset(
        name="Test Dataset",
    )
    
    assert dataset is not None, "Dataset creation failed"