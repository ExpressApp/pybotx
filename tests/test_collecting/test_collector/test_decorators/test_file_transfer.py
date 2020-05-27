from botx import SystemEvents

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_defining_file_handler_in_collector_as_decorator(
    handler_as_function, extract_collector, collector_cls
):
    collector = collector_cls()
    collector.file_transfer()(handler_as_function)
    assert SystemEvents(collector.handlers[0].body) == SystemEvents.file_transfer
