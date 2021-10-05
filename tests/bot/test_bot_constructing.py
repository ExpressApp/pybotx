import pytest

from botx import Bot


def test__bot__required_at_least_one_collector(
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Act -
    Bot(collectors=[], bot_accounts=[])

    # - Assert -
    assert "Bot should have at least one `HandlerCollector`" in loguru_caplog.text
    assert "Bot should have at least one `BotAccount`" in loguru_caplog.text
