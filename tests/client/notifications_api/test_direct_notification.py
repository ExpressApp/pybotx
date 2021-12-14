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
    BotIsNotChatMemberError,
    BubbleMarkup,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    HandlerCollector,
    IncomingMessage,
    KeyboardMarkup,
    Mention,
    OutgoingAttachment,
    OutgoingMessage,
    StealthModeDisabledError,
    UnknownBotAccountError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_account: BotAccount,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
                            "opts": {"silent": True},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
                            "opts": {"silent": True},
                        },
                    ],
                ],
            },
            "file": {
                "file_name": "test.txt",
                "data": "data:application/octet-stream;base64,SGVsbG8sIHdvcmxkIQo=",
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
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    payload = api_incoming_message_factory(
        bot_id=bot_id,
        host=host,
        group_chat_id="054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
        chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
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

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__answer_message__no_incoming_message_error_raised(
    host: str,
    bot_account: BotAccount,
    bot_id: UUID,
) -> None:
    # - Arrange -
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(AnswerDestinationLookupError) as exc:
            await bot.answer_message("Hi!")

    # - Assert -
    assert "No IncomingMessage received" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__answer_message__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_account: BotAccount,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
                            "opts": {"silent": True},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
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
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    payload = api_incoming_message_factory(
        bot_id=bot_id,
        host=host,
        group_chat_id="054af49e-5e18-4dca-ad73-4f96b6de63fa",
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

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__unknown_bot_account_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    unknown_bot_id = UUID("51550ccc-dfd1-4d22-9b6f-a330145192b0")
    direct_notification_endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnknownBotAccountError) as exc:
            await bot.send_message(
                body="Hi!",
                bot_id=unknown_bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert not direct_notification_endpoint.called
    assert str(unknown_bot_id) in str(exc.value)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__chat_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                    "error_description": "Chat with specified id not found",
                },
            },
        )

    # - Assert -
    with pytest.raises(ChatNotFoundError) as exc:
        await task

    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__bot_is_not_a_chat_member_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "bot_is_not_a_chat_member",
                "errors": [],
                "error_data": {
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                    "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                    "error_description": "Bot is not a chat member",
                },
            },
        )

    # - Assert -
    with pytest.raises(BotIsNotChatMemberError) as exc:
        await task

    assert "bot_is_not_a_chat_member" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__event_recipients_list_is_empty_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "event_recipients_list_is_empty",
                "errors": [],
                "error_data": {
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                    "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                    "recipients_param": ["b165f00f-3154-412c-7f11-c120164257da"],
                    "error_description": "Event recipients list is empty",
                },
            },
        )

    # - Assert -
    with pytest.raises(FinalRecipientsListEmptyError) as exc:
        await task

    assert "event_recipients_list_is_empty" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__stealth_mode_disabled_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "stealth_mode_disabled",
                "errors": [],
                "error_data": {
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                    "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                    "error_description": "Stealth mode disabled in specified chat",
                },
            },
        )

    # - Assert -
    with pytest.raises(StealthModeDisabledError) as exc:
        await task

    assert "stealth_mode_disabled" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__miminally_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__maximum_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "botx.models.message.mentions.uuid4",
        lambda: UUID("f3e176d5-ff46-4b18-b260-25008338c06e"),
    )

    body = f"Hi, {Mention.user(UUID('8f3abcc8-ba00-4c89-88e0-b786beb8ec24'))}!"
    formatted_body = "Hi, @{mention:f3e176d5-ff46-4b18-b260-25008338c06e}!"

    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
            "recipients": ["41af5a7b-04c1-465e-8383-e3b1d9e76126"],
            "opts": {
                "stealth_mode": True,
                "notification_opts": {
                    "send": True,
                    "force_dnd": True,
                },
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body=body,
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
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

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_message__all_mentions_types_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    monkeypatch.setattr(
        "botx.models.message.mentions.uuid4",
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
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(
            bot.send_message(
                body=body,
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called
