import pytest

from botx.collecting.handlers.handler import Handler
from botx.dependencies.solving import get_executor


def test_error_when_creating_executor_without_call(build_handler):
    handler = Handler(build_handler(...), body="/body")
    dependant = handler.dependant
    dependant.call = None
    with pytest.raises(AssertionError):
        get_executor(dependant)
