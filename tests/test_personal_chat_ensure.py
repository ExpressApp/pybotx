from datetime import datetime as dt
from http import HTTPStatus
from typing import Any, Callable
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import ChatInfo, ChatInfoMember, ChatTypes, UserKinds
from tests.client.chats_api.factories import APIPersonalChatResponseFactory, ChatInfoFactory
from tests.testkit import BotXRequest, assert_deep_equal, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__ensure_personal_chat__returns_existing(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    api_response: Any = APIPersonalChatResponseFactory()  # type: ignore[no-untyped-call]
    request = BotXRequest(
        method="GET",
        path="/api/v1/botx/chats/personal",
        params={"user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364"},
    )
    endpoint = mock_botx(respx_mock, host, request, api_response, HTTPStatus.OK)

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.ensure_personal_chat(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    expected_chat_info = ChatInfoFactory(
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
    )  # type: ignore[no-untyped-call]

    assert_deep_equal(chat_info, expected_chat_info)
    assert endpoint.called


async def test__ensure_personal_chat__creates_when_missing(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    user_huid = UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364")
    created_chat_id = UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa")
    chat_name = "Personal Chat"

    personal_request = BotXRequest(
        method="GET",
        path="/api/v1/botx/chats/personal",
        params={"user_huid": str(user_huid)},
    )
    personal_endpoint = mock_botx(
        respx_mock,
        host,
        personal_request,
        error_payload(
            "chat_not_found",
            error_data={
                "user_huid": str(user_huid),
                "error_description": "Personal chat with specified user_huid is not found",
            },
        ),
        HTTPStatus.NOT_FOUND,
    )

    create_request = BotXRequest(
        method="POST",
        path="/api/v3/botx/chats/create",
        json={
            "name": chat_name,
            "description": None,
            "chat_type": "chat",
            "members": [str(user_huid)],
            "avatar": None,
        },
    )
    create_endpoint = mock_botx(
        respx_mock,
        host,
        create_request,
        ok_payload({"chat_id": str(created_chat_id)}),
        HTTPStatus.OK,
    )

    info_request = BotXRequest(
        method="GET",
        path="/api/v3/botx/chats/info",
        params={"group_chat_id": str(created_chat_id)},
    )
    info_endpoint = mock_botx(
        respx_mock,
        host,
        info_request,
        ok_payload(
            {
                "chat_type": "chat",
                "creator": str(user_huid),
                "description": None,
                "group_chat_id": str(created_chat_id),
                "inserted_at": "2019-08-29T11:22:48.358586Z",
                "members": [
                    {
                        "admin": True,
                        "user_huid": str(user_huid),
                        "user_kind": "user",
                    },
                ],
                "name": chat_name,
                "shared_history": False,
            }
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.ensure_personal_chat(
            bot_id=bot_id,
            user_huid=user_huid,
            name=chat_name,
        )

    # - Assert -
    assert_deep_equal(
        chat_info,
        ChatInfo(
            chat_type=ChatTypes.PERSONAL_CHAT,
            creator_id=user_huid,
            description=None,
            chat_id=created_chat_id,
            created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
            members=[
                ChatInfoMember(
                    is_admin=True,
                    huid=user_huid,
                    kind=UserKinds.RTS_USER,
                ),
            ],
            name=chat_name,
            shared_history=False,
        ),
    )
    assert personal_endpoint.called
    assert create_endpoint.called
    assert info_endpoint.called
