import pytest

from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_error_when_merging_handlers_with_equal_bodies(build_handler):
    collector1 = Collector()
    collector1.add_handler(
        handler=build_handler("handler1"), body="/body", name="handler1",
    )

    collector2 = Collector()
    collector2.add_handler(
        handler=build_handler("handler2"), body="/body", name="handler2",
    )

    with pytest.raises(AssertionError):
        collector1.include_collector(collector2)


def test_error_when_merging_handlers_with_equal_names(build_handler):
    collector1 = Collector()
    collector1.add_handler(
        handler=build_handler("handler1"), body="/body1", name="handler",
    )

    collector2 = Collector()
    collector2.add_handler(
        handler=build_handler("handler2"), body="/body2", name="handler",
    )

    with pytest.raises(AssertionError):
        collector1.include_collector(collector2)


def test_only_single_default_handler_can_defined_in_collector(default_handler):
    collector1 = Collector(default=default_handler)
    collector2 = Collector(default=default_handler)

    with pytest.raises(AssertionError):
        collector1.include_collector(collector2)
