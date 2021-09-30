from typing import Callable

import pytest

from botx import Bot, HandlerCollector, IncomingMessage, lifespan_wrapper
from botx.bot.handler import IncomingMessageHandlerFunc


@pytest.mark.asyncio
async def test_bot_state(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    async def middleware(
        message: IncomingMessage,
        bot: Bot,
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        bot.state.api_token = "token"

        await call_next(message, bot)

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[], middlewares=[middleware])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert built_bot.state.api_token == "token"
