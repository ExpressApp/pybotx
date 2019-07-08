import pytest
from loguru import logger

from botx import BotXException, ChatCreatedData
from botx.helpers import create_message, get_headers, logger_wrapper


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


def test_headers_factory_for_botx_api():
    required_headers = {"authorization": "Bearer token"}

    headers = get_headers(token="token")
    for header, value in headers.items():
        if header in required_headers:
            required_value = required_headers.pop(header)
            assert value == required_value

    assert required_headers == {}


def test_logger_wrapper_logs_exception(caplog):
    exc = Exception("test exception")

    logger.enable("botx")

    @logger_wrapper
    def func(*_):
        raise exc

    func(None, None)

    assert "test exception" in caplog.text
