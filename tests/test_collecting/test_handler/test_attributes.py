from botx.collecting.handler import Handler

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_handler_docstring_stored_as_full_description(handler_as_function):
    handler = Handler(body="/command", handler=handler_as_function)
    assert handler.full_description == handler_as_function.__doc__


def test_handler_from_function(handler_as_function):
    handler = Handler(body="/command", handler=handler_as_function)
    assert handler.name == "handler_function"


def test_name_when_name_was_passed_explicitly(handler_as_function):
    handler = Handler(handler=handler_as_function, body="/command", name="my_handler")
    assert handler.name == "my_handler"


def test_any_body_for_hidden_handler(handler_as_function):
    Handler(handler=handler_as_function, body="any text!", include_in_status=False)
