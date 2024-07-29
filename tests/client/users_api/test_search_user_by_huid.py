from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    UserFromSearch,
    UserNotFoundError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_huid__user_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/users/by_huid",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "user_not_found",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UserNotFoundError) as exc:
            await bot.search_user_by_huid(
                bot_id=bot_id,
                huid=UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"),
            )

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


async def test__search_user_by_huid__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: Dict[str, Any],
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/users/by_huid",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": user_from_search_with_data_json,
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        user = await bot.search_user_by_huid(
            bot_id=bot_id,
            huid=UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"),
        )

    # - Assert -
    assert user == user_from_search_with_data

    assert endpoint.called


async def test__search_user_by_huid_without_data__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    user_from_search_without_data: UserFromSearch,
    user_from_search_without_data_json: Dict[str, Any],
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/users/by_huid",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": user_from_search_without_data_json,
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        user = await bot.search_user_by_huid(
            bot_id=bot_id,
            huid=UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"),
        )

    # - Assert -
    assert user == user_from_search_without_data

    assert endpoint.called
