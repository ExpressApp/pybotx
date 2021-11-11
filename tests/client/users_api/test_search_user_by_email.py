from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, lifespan_wrapper
from botx.client.users_api.exceptions import UserNotFoundError
from botx.client.users_api.models import UserFromSearch


@respx.mock
@pytest.mark.asyncio
async def test__search_user_by_email__user_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_email = "ad_user@cts.com"

    endpoint = respx.get(
        f"https://{host}/api/v3/botx/users/by_email",
        headers={"Authorization": "Bearer token"},
        params={"email": user_email},
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UserNotFoundError) as exc:
            await bot.search_user_by_email(bot_id, user_email)

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__search_user_by_email__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_email = "ad_user@cts.com"
    result = {
        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        "ad_login": "ad_user_login",
        "ad_domain": "cts.com",
        "name": "Bob",
        "company": "Bobs Co",
        "company_position": "Director",
        "department": "Owners",
        "emails": [user_email],
    }
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/users/by_email",
        headers={"Authorization": "Bearer token"},
        params={"email": user_email},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok", "result": result},
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        user = await bot.search_user_by_email(bot_id, user_email)

    # - Assert -
    assert user == UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=[user_email],
    )

    assert endpoint.called
