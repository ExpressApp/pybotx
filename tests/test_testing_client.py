import asyncio

import pytest

from botx import (
    Bot,
    BotXAPIError,
    IncomingMessage,
    Message,
    SendingMessage,
    UpdatePayload,
    testing,
)


def test_regenerating_app_for_errored_views(bot: Bot) -> None:
    with testing.TestClient(bot) as client:
        original_mock = client.bot.client.http_client
        client.generate_error_api = True

        assert original_mock != client.bot.client.http_client


@pytest.mark.asyncio
async def test_disabling_sync_send_for_client(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    @bot.handler  # pragma: no cover
    async def background_handler() -> None:
        await asyncio.sleep(5)

    incoming_message.command.body = "/background-handler"

    with testing.TestClient(bot) as client:
        await client.send_command(incoming_message, False)

        assert bot._tasks

    await bot.shutdown()


@pytest.mark.asyncio
async def test_sending_command_result_when_token_errored(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    with testing.TestClient(bot, generate_error_api=True):
        with pytest.raises(BotXAPIError):
            await bot.send(
                SendingMessage.from_message(
                    text="some text",
                    message=Message.from_dict(incoming_message.dict(), bot),
                )
            )


@pytest.mark.asyncio
async def test_sending_notification_to_errored_api(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    bot._get_cts_by_host(incoming_message.user.host).server_credentials.token = "token"
    with testing.TestClient(bot, generate_error_api=True):
        with pytest.raises(BotXAPIError):
            sending_msg = SendingMessage.from_message(
                text="some text",
                message=Message.from_dict(incoming_message.dict(), bot),
            )
            sending_msg.sync_id = None
            await bot.send(sending_msg)


@pytest.mark.asyncio
async def test_sending_command_result_to_errored_api(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    bot._get_cts_by_host(incoming_message.user.host).server_credentials.token = "token"

    with testing.TestClient(bot, generate_error_api=True):
        with pytest.raises(BotXAPIError):
            await bot.send(
                SendingMessage.from_message(
                    text="some text",
                    message=Message.from_dict(incoming_message.dict(), bot),
                )
            )


@pytest.mark.asyncio
async def test_sending_event_update_to_errored_api(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    bot._get_cts_by_host(incoming_message.user.host).server_credentials.token = "token"

    with testing.TestClient(bot, generate_error_api=True):
        with pytest.raises(BotXAPIError) as error:
            await bot.update_message(
                Message.from_dict(incoming_message.dict(), bot).credentials,
                UpdatePayload(text="some text"),
            )
