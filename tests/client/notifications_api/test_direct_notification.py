import asyncio
from http import HTTPStatus
from typing import Any
from collections.abc import Callable, Sequence
from uuid import UUID

import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import (
    build_bot,
    AnswerDestinationLookupError,
    Bot,
    BotIsNotChatMemberError,
    BubbleMarkup,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    HandlerCollector,
    IncomingMessage,
    KeyboardMarkup,
    MentionBuilder,
    NotificationBodyTooLongError,
    OutgoingAttachment,
    OutgoingMessage,
    StealthModeDisabledError,
    UnknownBotAccountError,
)
from pybotx.presentation.raw_handlers import (
    async_execute_raw_bot_command,
    set_raw_botx_method_result,
)

from pybotx.testkit import BotXRequest, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v4/botx/notifications/direct"
CHAT_ID = "054af49e-5e18-4dca-ad73-4f96b6de63fa"
SYNC_ID = "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"

BASE_REQUEST = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "group_chat_id": CHAT_ID,
        "notification": {"status": "ok", "body": "Hi!"},
    },
)


async def test__send__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "opts": {
                    "silent_response": True,
                    "buttons_auto_adjust": True,
                },
                "status": "ok",
                "body": "Hi!",
                "metadata": {"foo": "bar"},
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "data": {},
                            "label": "Bubble button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
            "file": {
                "file_name": "test.txt",
                "data": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
            },
            "recipients": ["0a462a79-d9a2-4fad-8a96-7074f59daba9"],
            "opts": {
                "stealth_mode": True,
                "notification_opts": {
                    "send": True,
                    "force_dnd": True,
                },
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    payload = api_incoming_message_factory(
        bot_id=bot_id,
        host=host,
        group_chat_id=CHAT_ID,
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

    outgoing_message = OutgoingMessage(
        bot_id=bot_id,
        chat_id=UUID(CHAT_ID),
        body="Hi!",
        metadata={"foo": "bar"},
        bubbles=bubbles,
        keyboard=keyboard,
        file=file,
        silent_response=True,
        markup_auto_adjust=True,
        recipients=[UUID("0a462a79-d9a2-4fad-8a96-7074f59daba9")],
        stealth_mode=True,
        send_push=True,
        ignore_mute=True,
    )

    @collector.command("/hello", description="Hello command")
    async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send(message=outgoing_message)

    # - Act -
    async with bot_factory(collectors=[collector]) as bot:
        async_execute_raw_bot_command(bot, payload, verify_request=False)

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert endpoint.called


async def test__answer_message__no_incoming_message_error_raised(
    bot_factory: Any,
) -> None:
    # - Arrange -

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(AnswerDestinationLookupError) as exc:
            await bot.answer_message("Hi!")

    # - Assert -
    assert "No IncomingMessage received" in str(exc.value)


async def test__answer_message__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "metadata": {"foo": "bar"},
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "data": {},
                            "label": "Bubble button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
            "file": {
                "file_name": "test.txt",
                "data": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    payload = api_incoming_message_factory(
        bot_id=bot_id,
        host=host,
        group_chat_id=CHAT_ID,
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
        await bot.answer_message(
            "Hi!",
            metadata={"foo": "bar"},
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
        )

    # - Act -
    async with bot_factory(collectors=[collector]) as bot:
        async_execute_raw_bot_command(bot, payload, verify_request=False)

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert endpoint.called


async def test__send_message__unknown_bot_account_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_factory: Any,
) -> None:
    # - Arrange -
    unknown_bot_id = UUID("51550ccc-dfd1-4d22-9b6f-a330145192b0")
    endpoint = mock_botx(
        respx_mock,
        host,
        BASE_REQUEST,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(UnknownBotAccountError) as exc:
            await bot.send_message(
                body="Hi!",
                bot_id=unknown_bot_id,
                chat_id=UUID(CHAT_ID),
            )

    # - Assert -
    assert str(unknown_bot_id) in str(exc.value)
    assert not endpoint.called


@pytest.mark.parametrize(
    ("reason", "error_data", "expected_exc", "expected_fragments"),
    [
        (
            "chat_not_found",
            {
                "group_chat_id": CHAT_ID,
                "error_description": "Chat with specified id not found",
            },
            ChatNotFoundError,
            ("chat_not_found",),
        ),
        (
            "bot_is_not_a_chat_member",
            {
                "group_chat_id": CHAT_ID,
                "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                "error_description": "Bot is not a chat member",
            },
            BotIsNotChatMemberError,
            ("bot_is_not_a_chat_member",),
        ),
        (
            "event_recipients_list_is_empty",
            {
                "group_chat_id": CHAT_ID,
                "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                "recipients_param": ["b165f00f-3154-412c-7f11-c120164257da"],
                "error_description": "Event recipients list is empty",
            },
            FinalRecipientsListEmptyError,
            ("event_recipients_list_is_empty",),
        ),
        (
            "stealth_mode_disabled",
            {
                "group_chat_id": CHAT_ID,
                "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                "error_description": "Stealth mode disabled in specified chat",
            },
            StealthModeDisabledError,
            ("stealth_mode_disabled",),
        ),
    ],
)
async def test__send_message__callback_error_raised(
    reason: str,
    error_data: dict[str, Any],
    expected_exc: type[Exception],
    expected_fragments: Sequence[str],
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        BASE_REQUEST,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "error",
                "sync_id": SYNC_ID,
                "reason": reason,
                "errors": [],
                "error_data": error_data,
            },
            verify_request=False,
        )

    # - Assert -
    with pytest.raises(expected_exc) as exc:
        await task

    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__send_message__miminally_filled_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        BASE_REQUEST,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


async def test__send_message__maximum_filled_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
    bot_factory: Any,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "pybotx.infrastructure.contracts.message.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    body = f"Hi, {MentionBuilder.user(UUID('8f3abcc8-ba00-4c89-88e0-b786beb8ec24'))}!"
    formatted_body = "Hi, @{mention:f3e176d5-ff46-4b18-b260-25008338c06e}!"

    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "opts": {
                    "silent_response": True,
                    "buttons_auto_adjust": True,
                },
                "status": "ok",
                "body": formatted_body,
                "metadata": {"foo": "bar"},
                "bubble": [
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
                                "align": "center",
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
                                "align": "center",
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
                "data": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
            },
            "recipients": ["41af5a7b-04c1-465e-8383-e3b1d9e76126"],
            "opts": {
                "stealth_mode": True,
                "notification_opts": {
                    "send": True,
                    "force_dnd": True,
                },
            },
        },
    )

    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
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
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body=body,
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
                metadata={"foo": "bar"},
                bubbles=bubbles,
                keyboard=keyboard,
                file=file,
                silent_response=True,
                markup_auto_adjust=True,
                recipients=[UUID("41af5a7b-04c1-465e-8383-e3b1d9e76126")],
                stealth_mode=True,
                send_push=True,
                ignore_mute=True,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


async def test__send_message__all_mentions_types_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
    bot_factory: Any,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "pybotx.infrastructure.contracts.message.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    mentioned_user_huid = UUID("8f3abcc8-ba00-4c89-88e0-b786beb8ec24")
    user_mention = MentionBuilder.user(mentioned_user_huid)
    mentioned_contact_huid = UUID("1e0529fd-f091-4be9-93cc-6704a8957432")
    contact_mention = MentionBuilder.contact(mentioned_contact_huid)
    mentioned_chat_huid = UUID("454d73ad-1d32-4939-a708-e14b77414e86")
    chat_mention = MentionBuilder.chat(mentioned_chat_huid, "Our chat")
    mentioned_channel_huid = UUID("78198bec-3285-48d0-9fe2-c0eb3afaffd7")
    channel_mention = MentionBuilder.channel(mentioned_channel_huid)
    all_mention = MentionBuilder.all()

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

    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
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
        },
    )

    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body=body,
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


async def test__send_message__message_body_max_length_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    too_long_body = "1" * 4097
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {"status": "ok", "body": too_long_body},
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(NotificationBodyTooLongError) as exc:
            await bot.send_message(
                body=too_long_body,
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
            )

    # - Assert -
    assert "Message body length exceeds 4096 symbols" in str(exc.value)
    assert not endpoint.called


async def test__send_message__message_body_max_length_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    max_long_body = "1" * 4096
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {"status": "ok", "body": max_long_body},
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body=max_long_body,
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called
