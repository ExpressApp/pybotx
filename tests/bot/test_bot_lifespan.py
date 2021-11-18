import asyncio
from typing import Callable
from unittest.mock import Mock
from uuid import UUID

import pytest

from botx import Bot, BotAccount, HandlerCollector, IncomingMessage


@pytest.mark.asyncio
async def test__shutdown__wait_for_active_handlers(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        await asyncio.sleep(0)  # Return control to event loop
        correct_handler_trigger()

    bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    bot.async_execute_bot_command(user_command)
    await bot.shutdown()

    # - Assert -
    correct_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test__startup__authorize_cant_get_token(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccount,
    host: str,
    bot_id: UUID,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    await bot.startup()

    # - Assert -
    assert "Can't get token for bot account: " in loguru_caplog.text
    assert f"host - {host}, bot_id - {bot_id}" in loguru_caplog.text

    # Close httpx client
    await bot.shutdown()