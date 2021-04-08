from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_default_handler_after_including_into_another_collector(
    default_handler,
    handler_as_function,
):
    collector1 = Collector()
    collector2 = Collector(default=default_handler)

    collector1.include_collector(collector2)

    assert collector1.default_message_handler == collector2.default_message_handler
