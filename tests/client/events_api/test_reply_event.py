from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BubbleMarkup,
    HandlerCollector,
    KeyboardMarkup,
    MentionBuilder,
    OutgoingAttachment,
    ReplyMessage,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

REPLY_SYNC_ID = UUID("cd41d98a-f8a6-5ee8-b348-dff8c77229b2")


async def test__reply_message__minimal_filled_reply_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/events/reply_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "source_sync_id": "8ba66c5b-40bf-5c77-911d-519cb4e382e9",
            "reply": {
                "status": "ok",
                "body": "Replied",
            },
            "opts": {"raw_mentions": True},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(REPLY_SYNC_ID)},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        reply_sync_id = await bot.reply_message(
            bot_id=bot_id,
            sync_id=UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9"),
            body="Replied",
        )

    # - Assert -
    assert endpoint.called
    assert reply_sync_id == REPLY_SYNC_ID


@pytest.mark.parametrize("use_message_object", [False, True])
async def test__reply__v3_returns_none(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    use_message_object: bool,
) -> None:
    source_sync_id = UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9")
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/events/reply_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "source_sync_id": str(source_sync_id),
            "reply": {"status": "ok", "body": "Replied"},
            "opts": {"raw_mentions": True},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={"status": "ok", "result": "bot_reply_pushed"},
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    async with lifespan_wrapper(built_bot) as bot:
        if use_message_object:
            message = ReplyMessage(
                bot_id=bot_id, sync_id=source_sync_id, body="Replied"
            )
            reply_sync_id = await bot.reply(message=message, api_version=3)
        else:
            reply_sync_id = await bot.reply_message(
                bot_id=bot_id,
                sync_id=source_sync_id,
                body="Replied",
                api_version=3,
            )

    assert endpoint.call_count == 1
    assert reply_sync_id is None


@pytest.mark.parametrize("api_version", [5, 3.0])
async def test__reply_message__unsupported_api_version(
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    api_version: int | float,
) -> None:
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError, match="Unsupported reply event API version"):
            await bot.reply_message(
                bot_id=bot_id,
                sync_id=UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9"),
                body="Replied",
                api_version=api_version,  # type: ignore[arg-type]
            )


async def test__reply_message__maximum_filled_reply_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "pybotx.models.message.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/events/reply_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "source_sync_id": "8ba66c5b-40bf-5c77-911d-519cb4e382e9",
            "reply": {
                "status": "ok",
                "body": "@{mention:f3e176d5-ff46-4b18-b260-25008338c06e}!",
                "metadata": {"message": "metadata"},
                "opts": {
                    "buttons_auto_adjust": True,
                    "silent_response": True,
                },
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "label": "Bubble button",
                            "data": {},
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "label": "Keyboard button",
                            "data": {},
                            "opts": {"silent": True, "align": "center"},
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
                "data": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
            },
            "opts": {
                "raw_mentions": True,
                "stealth_mode": True,
                "notification_opts": {"send": True, "force_dnd": True},
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(REPLY_SYNC_ID)},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    bubbles = BubbleMarkup()
    bubbles.add_button(command="/bubble-button", label="Bubble button")

    keyboard = KeyboardMarkup()
    keyboard.add_button(command="/keyboard-button", label="Keyboard button")

    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        reply_sync_id = await bot.reply_message(
            bot_id=bot_id,
            sync_id=UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9"),
            body=f"{MentionBuilder.user(UUID('8f3abcc8-ba00-4c89-88e0-b786beb8ec24'))}!",
            metadata={"message": "metadata"},
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=True,
            markup_auto_adjust=True,
            stealth_mode=True,
            send_push=True,
            ignore_mute=True,
        )

    # - Assert -
    assert endpoint.called
    assert reply_sync_id == REPLY_SYNC_ID


async def test__reply__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "pybotx.models.message.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/events/reply_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "source_sync_id": "8ba66c5b-40bf-5c77-911d-519cb4e382e9",
            "reply": {
                "status": "ok",
                "body": "@{mention:f3e176d5-ff46-4b18-b260-25008338c06e}!",
                "metadata": {"message": "metadata"},
                "opts": {
                    "buttons_auto_adjust": True,
                    "silent_response": True,
                },
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "label": "Bubble button",
                            "data": {},
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "label": "Keyboard button",
                            "data": {},
                            "opts": {"silent": True, "align": "center"},
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
                "data": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
            },
            "opts": {
                "raw_mentions": True,
                "stealth_mode": True,
                "notification_opts": {"send": True, "force_dnd": True},
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(REPLY_SYNC_ID)},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    bubbles = BubbleMarkup()
    bubbles.add_button(command="/bubble-button", label="Bubble button")

    keyboard = KeyboardMarkup()
    keyboard.add_button(command="/keyboard-button", label="Keyboard button")

    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    message = ReplyMessage(
        bot_id=bot_id,
        sync_id=UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9"),
        body=f"{MentionBuilder.user(UUID('8f3abcc8-ba00-4c89-88e0-b786beb8ec24'))}!",
        metadata={"message": "metadata"},
        bubbles=bubbles,
        keyboard=keyboard,
        file=file,
        silent_response=True,
        markup_auto_adjust=True,
        stealth_mode=True,
        send_push=True,
        ignore_mute=True,
    )
    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        reply_sync_id = await bot.reply(message=message)

    # - Assert -
    assert endpoint.called
    assert reply_sync_id == REPLY_SYNC_ID
