pytest_plugins = ("tests.test_collecting.fixtures",)


def test_defining_hidden_handler_in_collector_as_decorator(
    handler_as_function,
    extract_collector,
    collector_cls,
):
    collector = collector_cls()
    collector.hidden()(handler_as_function)
    assert not collector.handlers[0].include_in_status
