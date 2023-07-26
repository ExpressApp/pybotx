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
    lifespan_wrapper,
)
from pybotx.models.enums import UserKinds

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
                "result": [
                    {
                        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "ad_login": "ad_user_login",
                        "ad_domain": "cts.com",
                        "name": "Bob",
                        "company": "Bobs Co",
                        "company_position": "Director",
                        "department": "Owners",
                        "emails": user_emails,
                        "user_kind": "cts_user",
                    },
                ],
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
    assert users[0] == UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=user_emails,
        other_id=None,
        user_kind=UserKinds.CTS_USER,
    )

    assert endpoint.called
