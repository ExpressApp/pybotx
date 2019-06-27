import pytest

from botx import BotXException


def test_exception_empty_message():
    error_message = "error"
    error_data = {"key": "value"}
    with pytest.raises(BotXException) as e:
        raise BotXException(error_message, data=error_data)

    assert f"[msg] -> {error_message}" in str(e.value)
    assert "[data] ->" in str(e.value)

    try:
        raise BotXException(error_message, data=error_data)
    except BotXException as e:
        assert e.message == error_message
        assert e.data == error_data
