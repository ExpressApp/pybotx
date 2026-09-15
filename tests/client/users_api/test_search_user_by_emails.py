from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import UserFromSearch
from tests.testkit import BotXRequest, assert_deep_equal, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_email__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    user_emails = ["ad_user@cts.com"]

    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"emails": user_emails},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload([user_from_search_with_data_json]),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        users = await bot.search_user_by_emails(
            bot_id=bot_id,
            emails=user_emails,
        )

    # - Assert -
    assert_deep_equal(users, [user_from_search_with_data])
    assert endpoint.called


async def test__search_user_by_email_without_data__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_without_data: UserFromSearch,
    user_from_search_without_data_json: dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    user_emails = ["ad_user@cts.com"]

    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"emails": user_emails},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload([user_from_search_without_data_json]),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        users = await bot.search_user_by_emails(
            bot_id=bot_id,
            emails=user_emails,
        )

    # - Assert -
    assert_deep_equal(users, [user_from_search_without_data])
    assert endpoint.called


async def test__search_user_by_email_with_trusts_search__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    user_emails = ["ad_user@cts.com"]

    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={
            "emails": user_emails,
            "trusts_search": True,
            "partial_response": True,
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload([user_from_search_with_data_json]),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        users = await bot.search_user_by_emails(
            bot_id=bot_id,
            emails=user_emails,
            trusts_search=True,
            partial_response=True,
        )

    # - Assert -
    assert_deep_equal(users, [user_from_search_with_data])
    assert endpoint.called
