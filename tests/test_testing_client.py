import asyncio

import pytest

from botx import Bot, IncomingMessage, Message, TestClient


@pytest.mark.asyncio
async def test_disabling_sync_send_for_client(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    @bot.handler  # pragma: no cover
    async def background_handler() -> None:
        await asyncio.sleep(0)

    incoming_message.command.body = "/background-handler"

    with TestClient(bot) as client:
        await client.send_command(incoming_message, False)

        assert bot._tasks

    await bot.shutdown()


@pytest.mark.asyncio
async def test_raising_error_for_client(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    bot.collector.default_message_handler = None

    @bot.default
    async def default_with_error() -> None:
        raise RuntimeError

    with TestClient(bot) as client:
        with pytest.raises(RuntimeError):
            await client.send_command(incoming_message)


@pytest.mark.asyncio
async def test_handling_error_for_client_if_handler_registered(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    error_raised = False

    bot.collector.default_message_handler = None

    @bot.default
    async def default_with_error() -> None:
        raise RuntimeError

    @bot.exception_handler(RuntimeError)
    async def runtime_error_handler(_exc: RuntimeError, _message: Message) -> None:
        nonlocal error_raised
        error_raised = True

    with TestClient(bot) as client:
        await client.send_command(incoming_message)

    assert error_raised
