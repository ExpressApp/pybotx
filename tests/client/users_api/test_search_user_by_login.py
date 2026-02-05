from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import UserFromSearch, UserNotFoundError
from tests.testkit import BotXRequest, assert_deep_equal, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_ad__user_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="GET",
        path="/api/v3/botx/users/by_login",
        params={"ad_login": "ad_user_login", "ad_domain": "cts.com"},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        error_payload("user_not_found"),
        HTTPStatus.NOT_FOUND,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(UserNotFoundError) as exc:
            await bot.search_user_by_ad(
                bot_id=bot_id,
                ad_login="ad_user_login",
                ad_domain="cts.com",
            )

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


async def test__search_user_by_ad__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: Dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="GET",
        path="/api/v3/botx/users/by_login",
        params={"ad_login": "ad_user_login", "ad_domain": "cts.com"},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload(user_from_search_with_data_json),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        user = await bot.search_user_by_ad(
            bot_id=bot_id,
            ad_login="ad_user_login",
            ad_domain="cts.com",
        )

    # - Assert -
    assert_deep_equal(user, user_from_search_with_data)
    assert endpoint.called


async def test__search_user_by_ad_without_data__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_without_data: UserFromSearch,
    user_from_search_without_data_json: Dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="GET",
        path="/api/v3/botx/users/by_login",
        params={"ad_login": "ad_user_login", "ad_domain": "cts.com"},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload(user_from_search_without_data_json),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        user = await bot.search_user_by_ad(
            bot_id=bot_id,
            ad_login="ad_user_login",
            ad_domain="cts.com",
        )

    # - Assert -
    assert_deep_equal(user, user_from_search_without_data)
    assert endpoint.called
