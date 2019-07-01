import logging
from unittest import mock

import pytest

from botx import BotXException, ChatCreatedData
from botx.helpers import create_message, get_headers, thread_logger_wrapper


def test_message_creator_creates_message_or_raise_exception(message_data):
    create_message(message_data())

    with pytest.raises(BotXException):
        create_message({})


def test_transformation_data_to_chat_created_data(message_data):
    message = create_message(message_data('system:chat_created'))

    assert isinstance(message.command.data, ChatCreatedData)


def test_headers_factory_for_botx_api():
    required_headers = {"authorization": "Bearer token"}

    headers = get_headers(token="token")
    for header, value in headers.items():
        if header in required_headers:
            required_value = required_headers.pop(header)
            assert value == required_value

    assert required_headers == {}


def test_thread_wrapper_logs_exception():
    logger = logging.getLogger("botx")
    with mock.patch.object(logger, "exception") as mock_exception:
        exc = Exception("test exception")

        @thread_logger_wrapper
        def func(*args):
            raise exc

        func(None, None)
        mock_exception.assert_called_once_with(exc)
