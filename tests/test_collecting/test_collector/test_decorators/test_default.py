pytest_plugins = ("tests.test_collecting.fixtures",)


def test_defining_default_handler_in_collector_as_decorator(
    handler_as_function, extract_collector, collector_cls
):
    collector = collector_cls()
    collector.default()(handler_as_function)
    assert extract_collector(collector).default_message_handler
