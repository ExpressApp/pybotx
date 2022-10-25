from http import HTTPStatus
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
from pybotx.models.enums import UserKinds

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_other_id__user_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/users/by_other_id",
        headers={"Authorization": "Bearer token"},
        params={"other_id": "some_id"},
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
            await bot.search_user_by_other_id(
                bot_id=bot_id,
                other_id="some_id",
            )

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


async def test__search_user_by_other_id__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/users/by_other_id",
        headers={"Authorization": "Bearer token"},
        params={"other_id": "some_id"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                    "ad_login": "ad_user_login",
                    "ad_domain": "cts.com",
                    "name": "Bob",
                    "company": "Bobs Co",
                    "company_position": "Director",
                    "department": "Owners",
                    "emails": ["ad_user@cts.com"],
                    "other_id": "some_id",
                    "user_kind": "cts_user",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        user = await bot.search_user_by_other_id(
            bot_id=bot_id,
            other_id="some_id",
        )

    # - Assert -
    assert user == UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=["ad_user@cts.com"],
        other_id="some_id",
        user_kind=UserKinds.CTS_USER,
    )

    assert endpoint.called
