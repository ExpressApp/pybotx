import asyncio
from typing import Callable
from unittest.mock import Mock

import pytest

from botx import Bot, HandlerCollector, IncomingMessage


@pytest.mark.asyncio
async def test_wait_active_handlers(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        await asyncio.sleep(0)  # Return control to event loop
        right_handler_trigger()

    bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    bot.async_execute_bot_command(user_command)
    await bot.shutdown()

    # - Assert -
    right_handler_trigger.assert_called_once()
