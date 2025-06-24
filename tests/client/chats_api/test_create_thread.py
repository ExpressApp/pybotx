from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    ThreadCreationError,
    ThreadCreationEventNotFoundError,
    ThreadCreationProhibitedError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "api/v3/botx/chats/create_thread"


async def test__create_chat__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    sync_id = "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"
    thread_id = "2a8c0d1e-c4d1-4308-b024-6e1a9f4a4b6d"
    endpoint = respx_mock.post(
        f"https://{host}/{ENDPOINT}",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={"sync_id": sync_id},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"thread_id": thread_id},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        created_thread_id = await bot.create_thread(bot_id=bot_id, sync_id=UUID(sync_id))

    # - Assert -
    assert str(created_thread_id) == thread_id
    assert endpoint.called


@pytest.mark.parametrize(
    "return_json, response_status, expected_exc_type",
    (
        (
            {
                "status": "error",
                "reason": "thread_creation_is_prohibited",
                "errors": ["This bot is not allowed to create thread"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "threads_not_enabled",
                "errors": ["Threads not enabled for this chat"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "bot_is_not_a_chat_member",
                "errors": ["This bot is not a chat member"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "can_not_create_for_personal_chat",
                "errors": ["This is personal chat"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "unsupported_event_type",
                "errors": ["This event type is unsupported"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "unsupported_chat_type",
                "errors": ["This chat type is unsupported"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "thread_already_created",
                "errors": ["Thread already created"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "no_access_for_message",
                "errors": ["There is no access for this message"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "event_in_stealth_mode",
                "errors": ["This event is in stealth mode"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "event_already_deleted",
                "errors": ["This event already deleted"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "event_not_found",
                "errors": ["Event not found"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.NOT_FOUND,
            ThreadCreationEventNotFoundError,
        ),
        (
            {
                "status": "error",
                "reason": "|specified reason|",
                "errors": ["|specified errors|"],
                "error_data": {},
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            ThreadCreationError,
        ),
    ),
)
async def test__create_thread__botx_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    return_json,
    response_status,
    expected_exc_type,
) -> None:
    # - Arrange -
    sync_id = "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"
    endpoint = respx_mock.post(
        f"https://{host}/{ENDPOINT}",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={"sync_id": sync_id},
    ).mock(return_value=httpx.Response(response_status, json=return_json))

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(expected_exc_type) as exc:
            await bot.create_thread(
                bot_id=bot_id, sync_id=UUID(sync_id)
            )

    # - Assert -
    assert endpoint.called
    assert return_json["reason"] in str(exc.value)
