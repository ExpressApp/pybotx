from datetime import datetime as dt
from http import HTTPStatus
from typing import Any
from collections.abc import Callable, Sequence
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import (
    build_bot,
    ChatInfo,
    ChatInfoMember,
    ChatNotFoundError,
    ChatTypes,
    UserKinds,
)
from pybotx.testkit import BotXRequest, assert_deep_equal, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/info"

REQUEST = BotXRequest(
    method="GET",
    path=ENDPOINT,
    params={"group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"},
)


@pytest.mark.parametrize(
    ("response_status", "response_json", "expected_exc", "expected_fragments"),
    [
        (
            HTTPStatus.NOT_FOUND,
            error_payload(
                "chat_not_found",
                error_data={
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "error_description": "Chat with id dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4 not found",
                },
            ),
            ChatNotFoundError,
            ("chat_not_found",),
        ),
    ],
)
async def test__chat_info__error_response(
    response_status: int,
    response_json: dict[str, Any],
    expected_exc: type[Exception],
    expected_fragments: Sequence[str],
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(respx_mock, host, REQUEST, response_json, response_status)

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(expected_exc) as exc:
            await bot.chat_info(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__chat_info__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(
            {
                "chat_type": "group_chat",
                "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "description": None,
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                "inserted_at": "2019-08-29T11:22:48.358586Z",
                "members": [
                    {
                        "admin": True,
                        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "user_kind": "user",
                    },
                    {
                        "admin": False,
                        "user_huid": "705df263-6bfd-536a-9d51-13524afaab5c",
                        "user_kind": "botx",
                    },
                ],
                "name": "Group Chat Example",
                "shared_history": False,
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert_deep_equal(
        chat_info,
        ChatInfo(
            chat_type=ChatTypes.GROUP_CHAT,
            creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
            description=None,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
            members=[
                ChatInfoMember(
                    is_admin=True,
                    huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    kind=UserKinds.RTS_USER,
                ),
                ChatInfoMember(
                    is_admin=False,
                    huid=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                    kind=UserKinds.BOT,
                ),
            ],
            name="Group Chat Example",
            shared_history=False,
        ),
    )

    assert endpoint.called


async def test__chat_info__notes_chat_type_mapped_to_personal_chat(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(
            {
                "chat_type": "notes",
                "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "description": None,
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                "inserted_at": "2019-08-29T11:22:48.358586Z",
                "members": [
                    {
                        "admin": True,
                        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "user_kind": "user",
                    },
                ],
                "name": "Saved messages",
                "shared_history": False,
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert_deep_equal(
        chat_info,
        ChatInfo(
            chat_type=ChatTypes.PERSONAL_CHAT,
            creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
            description=None,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
            members=[
                ChatInfoMember(
                    is_admin=True,
                    huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    kind=UserKinds.RTS_USER,
                ),
            ],
            name="Saved messages",
            shared_history=False,
        ),
    )

    assert endpoint.called


async def test__chat_info__skipped_members(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    loguru_caplog: pytest.LogCaptureFixture,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(
            {
                "chat_type": "group_chat",
                "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "description": None,
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                "inserted_at": "2019-08-29T11:22:48.358586Z",
                "members": [
                    {
                        "admin": True,
                        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "user_kind": "user",
                    },
                    {
                        "admin": False,
                        "user_huid": "705df263-6bfd-536a-9d51-13524afaab5c",
                        "user_kind": "botx",
                    },
                    {
                        "admin": False,
                        "user_huid": "0843a8a8-6d56-4ce6-92aa-13dc36bd9ede",
                        "user_kind": "unsupported_user_type",
                    },
                ],
                "name": "Group Chat Example",
                "shared_history": False,
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert_deep_equal(
        chat_info,
        ChatInfo(
            chat_type=ChatTypes.GROUP_CHAT,
            creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
            description=None,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
            members=[
                ChatInfoMember(
                    is_admin=True,
                    huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    kind=UserKinds.RTS_USER,
                ),
                ChatInfoMember(
                    is_admin=False,
                    huid=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                    kind=UserKinds.BOT,
                ),
            ],
            name="Group Chat Example",
            shared_history=False,
        ),
    )
    assert "One or more unsupported user types skipped" in loguru_caplog.text
    assert endpoint.called


async def test__open_channel_info__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        BotXRequest(
            method="GET",
            path=ENDPOINT,
            params={"group_chat_id": "e53d5080-68f7-5050-bb4f-005efd375612"},
        ),
        ok_payload(
            {
                "chat_type": "channel",
                "creator": None,
                "description": None,
                "group_chat_id": "e53d5080-68f7-5050-bb4f-005efd375612",
                "inserted_at": "2023-10-26T07:49:53.821672Z",
                "members": [
                    {
                        "admin": True,
                        "server_id": "a619fcfa-a19b-5256-a592-9b0e75ca0896",
                        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "user_kind": "cts_user",
                    },
                    {
                        "admin": False,
                        "user_huid": "705df263-6bfd-536a-9d51-13524afaab5c",
                        "server_id": "a619fcfa-a19b-5256-a592-9b0e75ca0896",
                        "user_kind": "botx",
                    },
                ],
                "name": "Open Channel Example",
                "shared_history": False,
                "updated_at": "2023-10-26T08:09:30.721566Z",
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("e53d5080-68f7-5050-bb4f-005efd375612"),
        )

    # - Assert -
    assert_deep_equal(
        chat_info,
        ChatInfo(
            chat_type=ChatTypes.CHANNEL,
            creator_id=None,
            description=None,
            chat_id=UUID("e53d5080-68f7-5050-bb4f-005efd375612"),
            created_at=datetime_formatter("2023-10-26T07:49:53.821672Z"),
            members=[
                ChatInfoMember(
                    is_admin=True,
                    huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    kind=UserKinds.CTS_USER,
                ),
                ChatInfoMember(
                    is_admin=False,
                    huid=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                    kind=UserKinds.BOT,
                ),
            ],
            name="Open Channel Example",
            shared_history=False,
        ),
    )

    assert endpoint.called
