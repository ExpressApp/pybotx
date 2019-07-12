import pytest

from botx import BotXException, ChatCreatedData
from botx.helpers import create_message, is_coroutine_callable


class TestCreateMessageHelper:
    def test_message_creator_creates_message_or_raise_exception(self, message_data):
        create_message(message_data())

        with pytest.raises(BotXException):
            create_message({})

    def test_transformation_data_to_chat_created_data(self, message_data):
        message = create_message(message_data("system:chat_created"))

        assert isinstance(message.command.data, ChatCreatedData)

    def test_that_only_known_system_events_are_transformed(self, message_data):
        msg = message_data("system:chat_created2")
        msg["command"]["command_type"] = "system"

        message = create_message(msg)

        assert isinstance(message.command.data, dict)


def test_check_class_is_coroutine():
    class TestClass:
        pass

    assert not is_coroutine_callable(TestClass)


def test_check_class_instance_call_is_coroutine():
    class TestClass:
        async def __call__(self):
            pass

    assert is_coroutine_callable(TestClass())
