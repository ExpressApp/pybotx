import pytest

from botx.exceptions import NoMatchFound

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_raising_exception_when_searching_for_handler_and_no_found(collector_cls):
    collector = collector_cls()
    with pytest.raises(NoMatchFound):
        collector.handler_for("not-existing-handler")
