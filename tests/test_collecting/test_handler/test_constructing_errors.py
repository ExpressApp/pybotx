import pytest
from pydantic import ValidationError

from botx.collecting.handlers.handler import Handler

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_error_handler_from_class(handler_as_class):
    with pytest.raises(ValidationError):
        Handler(body="/command", handler=handler_as_class)


def test_error_from_callable(handler_as_callable_object):
    with pytest.raises(ValidationError):
        Handler(body="/command", handler=handler_as_callable_object)


def test_slash_in_command_for_public_command(handler_as_function):
    with pytest.raises(ValidationError):
        Handler(body="command", handler=handler_as_function)


def test_only_one_slash_in_public_command(handler_as_function):
    with pytest.raises(ValidationError):
        Handler(body="//command", handler=handler_as_function)


def test_that_menu_command_contain_only_single_word(handler_as_function):
    with pytest.raises(ValidationError):
        Handler(body="/many words handler", handler=handler_as_function)
