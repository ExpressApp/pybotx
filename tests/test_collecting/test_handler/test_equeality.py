from botx.collecting.handler import Handler

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_equality_is_false_if_not_handler_passed(handler_as_function):
    handler = Handler(body="/command", handler=handler_as_function)
    assert handler != ""


def test_equality_is_false_if_handlers_are_different(handler_as_function):
    handler1 = Handler(body="/command1", handler=handler_as_function)
    handler2 = Handler(body="/command2", handler=handler_as_function)
    assert handler1 != handler2


def test_equality_if_handlers_are_similar(handler_as_function):
    handler1 = Handler(body="/command", handler=handler_as_function)
    handler2 = Handler(body="/command", handler=handler_as_function)
    assert handler1 == handler2
