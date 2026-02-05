from collections.abc import Callable
from unittest.mock import Mock

import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotXAuthVersion,
    HandlerCollector,
    IncomingMessage,
)
from pybotx.bot.testing import lifespan_wrapper

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_execute_bot_command__wait_for_task_execution(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(bot):
        await bot.async_execute_bot_command(user_command)

        # - Assert -
        correct_handler_trigger.assert_called_once()


async def test__shutdown__wait_for_active_handlers(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    bot.async_execute_bot_command(user_command)
    await bot.shutdown()

    # - Assert -
    correct_handler_trigger.assert_called_once()


async def test__fetch_tokens__skips_for_auth_v2(
    respx_mock: MockRouter,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        auth_version=BotXAuthVersion.V2,
    )

    # - Act -
    await bot.fetch_tokens()

    # - Assert -
    assert len(respx_mock.calls) == 0

    # Cleanup
    await bot.shutdown()
