import pytest

from botx.models.datastructures import State


@pytest.fixture()
def storage():
    return State()
