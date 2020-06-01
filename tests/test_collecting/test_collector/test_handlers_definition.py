from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_collector_default_handler_generating(default_handler):
    collector = Collector(default=default_handler)

    assert collector.default_message_handler == default_handler
