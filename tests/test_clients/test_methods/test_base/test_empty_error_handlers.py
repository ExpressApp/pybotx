from botx.clients.methods.base import BotXMethod


class TestMethod(BotXMethod):
    __url__ = "/path/to/example"
    __method__ = "GET"
    __returning__ = str


def test_method_empty_error_handlers():
    test_method = TestMethod()

    assert test_method.__errors_handlers__ == {}
