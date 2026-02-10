from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import (
    build_bot,
    EventNotFoundError,
    ThreadAlreadyExistsError,
    ThreadCreationError,
    ThreadCreationProhibitedError,
)
from pybotx.testkit import BotXRequest, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/create_thread"


@pytest.fixture
def sync_id() -> str:
    return "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"


async def test__create_thread__succeed(
    respx_mock: MockRouter,
    host: str,
    sync_id: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(method="POST", path=ENDPOINT, json={"sync_id": sync_id})
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"thread_id": sync_id}),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        created_thread_id = await bot.create_thread(
            bot_id=bot_id,
            sync_id=UUID(sync_id),
        )

    # - Assert -
    assert str(created_thread_id) == sync_id
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
                "reason": "event_not_found",
                "errors": ["Event not found"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.NOT_FOUND,
            EventNotFoundError,
        ),
        (
            {
                "status": "error",
                "reason": "event_already_deleted",
                "errors": ["This event already deleted"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.CONFLICT,
            ThreadCreationError,
        ),
        (
            {
                "status": "error",
                "reason": "thread_already_created",
                "errors": ["Thread already created"],
                "error_data": {"bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46"},
            },
            HTTPStatus.CONFLICT,
            ThreadAlreadyExistsError,
        ),
        (
            {
                "status": "error",
                "reason": None,
                "errors": [],
                "error_data": {},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "errors": [],
                "error_data": {},
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "unexpected reason",
                "errors": [],
            },
            HTTPStatus.FORBIDDEN,
            ThreadCreationProhibitedError,
        ),
    ),
)
async def test__create_thread__botx_error_raised(
    respx_mock: MockRouter,
    host: str,
    sync_id: str,
    bot_id: UUID,
    bot_factory: Any,
    return_json: dict[str, Any],
    response_status: int,
    expected_exc_type: type[BaseException],
) -> None:
    # - Arrange -
    request = BotXRequest(method="POST", path=ENDPOINT, json={"sync_id": sync_id})
    endpoint = mock_botx(respx_mock, host, request, return_json, response_status)

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(expected_exc_type) as exc:
            await bot.create_thread(
                bot_id=bot_id,
                sync_id=UUID(sync_id),
            )

    # - Assert -
    assert endpoint.called

    if return_json.get("reason"):
        assert return_json["reason"] in str(exc.value)
