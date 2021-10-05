import pytest

from botx import Bot, BotAccount, HandlerCollector


def test__bot__empty_collectors_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccount,
) -> None:
    # - Act -
    Bot(collectors=[], bot_accounts=[bot_account])

    # - Assert -
    assert "Bot has no connected collectors" in loguru_caplog.text


def test__bot__empty_bot_accounts_warning(
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Act -
    Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Assert -
    assert "Bot has no bot accounts" in loguru_caplog.text
