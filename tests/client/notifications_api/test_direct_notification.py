import asyncio
from http import HTTPStatus
from typing import Any, Callable, Dict
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import (
    AnswerDestinationLookupError,
    Bot,
    BotAccount,
    BubbleMarkup,
    HandlerCollector,
    IncomingMessage,
    KeyboardMarkup,
    Mention,
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
        with pytest.raises(AnswerDestinationLookupError) as exc:
            await bot.answer("Hi!")

    # - Assert -
    assert "No IncomingMessage received" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__answer__succeed(
    httpx_client: httpx.AsyncClient,
    chat_id: UUID,
    host: str,
    sync_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "metadata": {"foo": "bar"},
                "bubbles": [
                    [
                        {
                            "command": "/bubble-button",
                            "label": "Bubble button",
                            "data": {},
                            "opts": {"silent": True},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "label": "Keyboard button",
                            "data": {},
                            "opts": {"silent": True},
                        },
                    ],
                ],
            },
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

    payload = incoming_message_payload_factory(
        bot_id=bot_id,
        host=host,
        group_chat_id=chat_id,
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/bubble-button",
        label="Bubble button",
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard-button",
        label="Keyboard button",
    )

    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    collector = HandlerCollector()

    @collector.command("/hello", description="Hello command")
    async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.answer(
            "Hi!",
            metadata={"foo": "bar"},
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
        )

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

        await asyncio.sleep(0)  # Return control to event loop

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
    monkeypatch: pytest.MonkeyPatch,
    mock_authorization: None,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "botx.client.notifications_api.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    body = f"Hi, {Mention.user(UUID('8f3abcc8-ba00-4c89-88e0-b786beb8ec24'))}!"
    formatted_body = "Hi, @{mention:f3e176d5-ff46-4b18-b260-25008338c06e}!"

    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {
                "status": "ok",
                "body": formatted_body,
                "metadata": {"foo": "bar"},
                "bubbles": [
                    [
                        {
                            "command": "/bubble-button",
                            "label": "Bubble button",
                            "data": {"foo": "bar"},
                            "opts": {
                                "silent": False,
                                "h_size": 1,
                                "alert_text": "Alert text 1",
                                "show_alert": True,
                                "handler": "client",
                            },
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "label": "Keyboard button",
                            "data": {"baz": "quux"},
                            "opts": {
                                "silent": True,
                                "h_size": 2,
                                "alert_text": "Alert text 2",
                                "show_alert": True,
                            },
                        },
                    ],
                ],
                "mentions": [
                    {
                        "mention_type": "user",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                        "mention_data": {
                            "user_huid": "8f3abcc8-ba00-4c89-88e0-b786beb8ec24",
                        },
                    },
                ],
            },
            "file": {
                "file_name": "test.txt",
                "data": "data:application/octet-stream;base64,SGVsbG8sIHdvcmxkIQo=",
            },
            "opts": {"raw_mentions": True},
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

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/bubble-button",
        label="Bubble button",
        data={"foo": "bar"},
        silent=False,
        width_ratio=1,
        alert="Alert text 1",
        process_on_client=True,
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard-button",
        label="Keyboard button",
        data={"baz": "quux"},
        silent=True,
        width_ratio=2,
        alert="Alert text 2",
        process_on_client=False,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message_id = await bot.send(
            body,
            bot_id=bot_id,
            chat_id=chat_id,
            metadata={"foo": "bar"},
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__send__all_mentions_types_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    monkeypatch: pytest.MonkeyPatch,
    mock_authorization: None,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "botx.client.notifications_api.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    mentioned_user_huid = UUID("8f3abcc8-ba00-4c89-88e0-b786beb8ec24")
    user_mention = Mention.user(mentioned_user_huid)
    mentioned_contact_huid = UUID("1e0529fd-f091-4be9-93cc-6704a8957432")
    contact_mention = Mention.contact(mentioned_contact_huid)
    mentioned_chat_huid = UUID("454d73ad-1d32-4939-a708-e14b77414e86")
    chat_mention = Mention.chat(mentioned_chat_huid, "Our chat")
    mentioned_channel_huid = UUID("78198bec-3285-48d0-9fe2-c0eb3afaffd7")
    channel_mention = Mention.channel(mentioned_channel_huid)
    all_mention = Mention.all()

    body = (
        f"Hi, {user_mention}, want you to know, "
        f"that I and {contact_mention} are getting married in a week. "
        f"Here's a chat for all the invitees: {chat_mention}. "
        f"And here is the news channel just in case: {channel_mention}. "
        "In case of something incredible, "
        f"I will notify you with {all_mention}, so you won't miss it."
    )

    formatted_body = (
        "Hi, @{mention:f3e176d5-ff46-4b18-b260-25008338c06e}, want you to know, "
        "that I and @@{mention:f3e176d5-ff46-4b18-b260-25008338c06e} are getting married in a week. "
        "Here's a chat for all the invitees: ##{mention:f3e176d5-ff46-4b18-b260-25008338c06e}. "
        "And here is the news channel just in case: ##{mention:f3e176d5-ff46-4b18-b260-25008338c06e}. "
        "In case of something incredible, "
        "I will notify you with @{mention:f3e176d5-ff46-4b18-b260-25008338c06e}, so you won't miss it."
    )

    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {
                "status": "ok",
                "body": formatted_body,
                "mentions": [
                    {
                        "mention_type": "user",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                        "mention_data": {
                            "user_huid": "8f3abcc8-ba00-4c89-88e0-b786beb8ec24",
                        },
                    },
                    {
                        "mention_type": "contact",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                        "mention_data": {
                            "user_huid": "1e0529fd-f091-4be9-93cc-6704a8957432",
                        },
                    },
                    {
                        "mention_type": "chat",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                        "mention_data": {
                            "group_chat_id": "454d73ad-1d32-4939-a708-e14b77414e86",
                            "name": "Our chat",
                        },
                    },
                    {
                        "mention_type": "channel",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                        "mention_data": {
                            "group_chat_id": "78198bec-3285-48d0-9fe2-c0eb3afaffd7",
                        },
                    },
                    {
                        "mention_type": "all",
                        "mention_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
                    },
                ],
            },
            "opts": {"raw_mentions": True},
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
            body,
            bot_id=bot_id,
            chat_id=chat_id,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called
