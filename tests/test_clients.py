import pytest

from botx import Bot


def test_client_validate_request_url_scheme(bot: Bot) -> None:
    with pytest.raises(ValueError):
        bot.client.scheme = "error"
