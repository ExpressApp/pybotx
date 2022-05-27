from http import HTTPStatus
from typing import Callable
from unittest.mock import Mock
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage
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


async def test__startup__authorize_cant_get_token(
    respx_mock: MockRouter,
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    # - Arrange -
    token_endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.UNAUTHORIZED,
            json={
                "status": "error",
            },
        ),
    )

    collector = HandlerCollector()

    bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    await bot.startup()

    # - Assert -
    assert token_endpoint.called

    assert "Can't get token for bot account: " in loguru_caplog.text
    assert f"host - {host}, bot_id - {bot_id}" in loguru_caplog.text

    # Cleanup
    await bot.shutdown()


async def test__startup__can_skip_fetching_tokens(
    respx_mock: MockRouter,
    bot_account: BotAccountWithSecret,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    # - Arrange -
    token_endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    )

    collector = HandlerCollector()

    bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    await bot.startup(fetch_tokens=False)

    # - Assert -
    assert not token_endpoint.called

    # Cleanup
    await bot.shutdown()
