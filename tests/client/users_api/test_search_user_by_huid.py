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
async def test__search_user_by_huid__user_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    user_huid: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/users/by_huid",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": user_huid},
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
            await bot.search_user_by_huid(bot_id, huid=user_huid)

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__search_user_by_huid__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    user_huid: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    result = {
        "user_huid": str(user_huid),
        "ad_login": "ad_user_login",
        "ad_domain": "cts.com",
        "name": "Bob",
        "company": "Bobs Co",
        "company_position": "Director",
        "department": "Owners",
        "emails": ["ad_user@cts.com"],
    }
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/users/by_huid",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": user_huid},
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
        user = await bot.search_user_by_huid(bot_id, huid=user_huid)

    # - Assert -
    assert user == UserFromSearch(
        huid=user_huid,
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=["ad_user@cts.com"],
    )

    assert endpoint.called
