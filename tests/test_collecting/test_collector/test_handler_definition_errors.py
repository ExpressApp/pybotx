import pytest
from pydantic import ValidationError

from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_handler_can_not_consist_from_slashes_only(handler_as_function):
    collector = Collector()
    with pytest.raises(ValidationError):
        collector.add_handler(handler_as_function, body="////")
