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
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_email__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: Dict[str, Any],
) -> None:
    # - Arrange -
    user_emails = ["ad_user@cts.com"]

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/users/by_email",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={"emails": user_emails},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": [user_from_search_with_data_json],
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        users = await bot.search_user_by_emails(
            bot_id=bot_id,
            emails=user_emails,
        )

    # - Assert -
    assert users[0] == user_from_search_with_data

    assert endpoint.called


async def test__search_user_by_email_without_data__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    user_from_search_without_data: UserFromSearch,
    user_from_search_without_data_json: Dict[str, Any],
) -> None:
    # - Arrange -
    user_emails = ["ad_user@cts.com"]

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/users/by_email",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={"emails": user_emails},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": [user_from_search_without_data_json],
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        users = await bot.search_user_by_emails(
            bot_id=bot_id,
            emails=user_emails,
        )

    # - Assert -
    assert users[0] == user_from_search_without_data

    assert endpoint.called
