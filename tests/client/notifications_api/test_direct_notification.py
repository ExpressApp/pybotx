import asyncio
from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    NoIncomingMessageError,
    OutgoingAttachment,
    UnknownBotAccountError,
    lifespan_wrapper,
)


@pytest.mark.asyncio
async def test__answer__no_incoming_message_error_raised(
    chat_id: UUID,
    host: str,
    sync_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(NoIncomingMessageError) as exc:
            await bot.answer("Hi!")

    # - Assert -
    assert "No IncomingMessage received" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__answer__succeed(
    chat_id: UUID,
    host: str,
    sync_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    payload = {
        "bot_id": bot_id,
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
        "async_files": [],
        "attachments": [],
        "source_sync_id": "bc3d06ed-7b2e-41ad-99f9-ca28adc2c88d",
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": "domain",
            "ad_login": "login",
            "app_version": "1.21.9",
            "chat_type": "chat",
            "device": "Firefox 91.0",
            "device_meta": {
                "permissions": {
                    "microphone": True,
                    "notifications": False,
                },
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": "Linux",
            "group_chat_id": chat_id,
            "host": host,
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": "Mozilla",
            "platform": "web",
            "platform_package_id": "ru.unlimitedtech.express",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": "Ivanov Ivan Ivanovich",
        },
        "proto_version": 4,
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

        await asyncio.sleep(0)  # Return control to event loop
        await bot.answer("Hi!")

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__send__unknown_bot_account_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    unknown_bot_id = UUID("51550ccc-dfd1-4d22-9b6f-a330145192b0")
    direct_notification_endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnknownBotAccountError) as exc:
            await bot.send(
                "Hi!",
                bot_id=unknown_bot_id,
                chat_id=chat_id,
            )

    # - Assert -
    assert not direct_notification_endpoint.called
    assert str(unknown_bot_id) in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__send__miminally_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message_id = await bot.send(
            "Hi!",
            bot_id=bot_id,
            chat_id=chat_id,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__send__maximum_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {"status": "ok", "body": "Hi!", "metadata": {"foo": "bar"}},
            "file": {
                "file_name": "test.txt",
                "data": "data:application/octet-stream;base64,SGVsbG8sIHdvcmxkIQo=",
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message_id = await bot.send(
            "Hi!",
            bot_id=bot_id,
            chat_id=chat_id,
            metadata={"foo": "bar"},
            file=file,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called
