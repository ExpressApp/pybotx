import pytest

from pybotx import Bot, BotAccountWithSecret, HandlerCollector
from pybotx import build_bot


def test__bot__empty_collectors_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    build_bot(collectors=[], bot_accounts=[bot_account])

    # - Assert -
    assert "Bot has no connected collectors" in loguru_caplog.text


def test__bot__empty_bot_accounts_warning(
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Act -
    build_bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Assert -
    assert "Bot has no bot accounts" in loguru_caplog.text
