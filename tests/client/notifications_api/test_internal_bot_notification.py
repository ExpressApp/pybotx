import asyncio
from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BotIsNotChatMemberError,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    HandlerCollector,
    RateLimitReachedError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_internal_bot_notification__rate_limit_reached_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/internal",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "data": {"foo": "bar"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.TOO_MANY_REQUESTS,
            json={
                "status": "error",
                "reason": "too_many_requests",
                "errors": [],
                "error_data": {
                    "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
                },
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
        with pytest.raises(RateLimitReachedError) as exc:
            await bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=chat_id,
                data={"foo": "bar"},
            )

    # - Assert -
    assert "too_many_requests" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_internal_bot_notification__chat_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/internal",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "data": {"foo": "bar"},
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
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=chat_id,
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": str(sync_id),
                    "error_description": f"Chat with id {sync_id!s} not found",
                },
            },
        )

    with pytest.raises(ChatNotFoundError) as exc:
        await task

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_internal_bot_notification__bot_is_not_chat_member_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/internal",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "data": {"foo": "bar"},
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
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=chat_id,
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "bot_is_not_a_chat_member",
                "errors": [],
                "error_data": {
                    "group_chat_id": str(chat_id),
                    "bot_id": str(bot_id),
                    "error_description": "Bot is not a chat member",
                },
            },
        )

    with pytest.raises(BotIsNotChatMemberError) as exc:
        await task

    # - Assert -
    assert "bot_is_not_a_chat_member" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_internal_bot_notification__final_recipients_list_empty_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/internal",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "data": {"foo": "bar"},
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
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=chat_id,
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "event_recipients_list_is_empty",
                "errors": [],
                "error_data": {
                    "group_chat_id": str(chat_id),
                    "bot_id": str(bot_id),
                    "recipients_param": ["b165f00f-3154-412c-7f11-c120164257da"],
                    "error_description": "Event recipients list is empty",
                },
            },
        )

    with pytest.raises(FinalRecipientsListEmptyError) as exc:
        await task

    # - Assert -
    assert "event_recipients_list_is_empty" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_internal_bot_notification__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/internal",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "data": {"foo": "bar"},
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
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=chat_id,
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": str(sync_id),
                "result": {},
            },
        )

    # - Assert -
    assert await task == sync_id
    assert endpoint.called
