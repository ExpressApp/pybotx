import pytest

from botx import Depends
from botx.collecting import Handler
from tests.conftest import HandlerClass, handler_function


class TestHandlerConstruction:
    def test_handler_from_function(self) -> None:
        handler = Handler(body="/command", handler=handler_function)
        assert handler.name == "handler_function"

    def test_error_handler_from_class(self) -> None:
        with pytest.raises(AssertionError):
            _ = Handler(body="/command", handler=HandlerClass)

    def test_error_from_callable_class_instance(self) -> None:
        with pytest.raises(AssertionError):
            _ = Handler(body="/command", handler=HandlerClass())

    def test_name_when_name_was_passed_explicitly(self) -> None:
        handler = Handler(body="/command", handler=handler_function, name="my_handler")
        assert handler.name == "my_handler"

    def test_slash_in_command_for_public_command(self) -> None:
        with pytest.raises(AssertionError):
            _ = Handler(body="command", handler=handler_function)

    def test_only_one_slash_in_public_command(self) -> None:
        with pytest.raises(AssertionError):
            _ = Handler(body="//command", handler=handler_function)

    def test_any_body_for_hidden_handler(self) -> None:
        handler = Handler(
            body="any text!", handler=handler_function, include_in_status=False
        )
        assert handler

    def test_sequence_in_dependencies(self) -> None:
        dependencies = [Depends(handler_function)]
        handler = Handler(
            body="/command", handler=handler_function, dependencies=dependencies
        )
        for dep in handler.dependencies:
            assert dep.dependency == handler_function

    def test_that_menu_command_contain_only_single_word(self) -> None:
        with pytest.raises(AssertionError):
            _ = Handler(body="/many words handler", handler=handler_function)
