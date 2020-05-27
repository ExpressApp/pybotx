from botx.exceptions import BotXException


def test_to_string_fills_template():
    exc = BotXException(arg=42)
    exc.message_template = "template with {arg}"

    assert str(exc) == "template with 42"
