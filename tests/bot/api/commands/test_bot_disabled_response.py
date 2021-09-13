from botx import build_bot_disabled_response


def test_build_bot_disabled_response() -> None:
    assert build_bot_disabled_response("some error") == {
        "error_data": {"status_message": "some error"},
        "errors": [],
        "reason": "bot_disabled",
    }
