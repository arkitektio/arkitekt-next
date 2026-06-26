""" SOme tests for the easy function in arkitekt_next. """

import pytest

from arkitekt_next import easy


@pytest.mark.integration
def test_easy() -> None:
    """Test the easy function from arkitekt_next."""
    with easy("johannes", "latest"):
        print("Hello world!")
