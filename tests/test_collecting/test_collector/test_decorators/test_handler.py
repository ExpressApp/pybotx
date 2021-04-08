from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_defining_handler_in_collector_as_decorator(
    handler_as_function,
    extract_collector,
    collector_cls,
):
    collector = Collector()
    collector.handler()(handler_as_function)
    handlers = [collector.handler_for("handler_function")]
    assert handlers
