import pytest

from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


@pytest.fixture()
def collector_with_handlers(handler_as_function):
    collector = Collector()
    for index in range(1, 31):
        body = "/{0}".format("a" * index)
        collector.add_handler(handler=handler_as_function, body=body, name=str(index))

    return collector


def test_sorting_handlers_in_collector_by_body_length(collector_with_handlers):
    added_handlers = collector_with_handlers._added_handlers
    assert added_handlers == sorted(
        added_handlers, key=lambda handler: len(handler.body), reverse=True
    )


def test_preserve_length_sort_when_merging_collectors(
    collector_with_handlers, handler_as_function
):
    collector = Collector()
    collector.add_handler(handler=handler_as_function, body="/{0}".format("a" * 1000))

    collector_with_handlers.include_collector(collector)

    added_handlers = collector_with_handlers._added_handlers
    assert added_handlers[0] == collector.handlers[0]
