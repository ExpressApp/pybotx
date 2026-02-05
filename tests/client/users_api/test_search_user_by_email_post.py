from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import UserFromSearch, UserNotFoundError
from pybotx.client.exceptions.http import (
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from tests.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__search_user_by_email_post__user_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
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
            await bot.search_user_by_email_post(
                bot_id=bot_id,
                email="ad_user@cts.com",
            )

    # - Assert -
    assert "user_not_found" in str(exc.value)
    assert endpoint.called


async def test__search_user_by_email_post__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_with_data: UserFromSearch,
    user_from_search_with_data_json: Dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
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
        user = await bot.search_user_by_email_post(
            bot_id=bot_id,
            email="ad_user@cts.com",
        )

    # - Assert -
    assert user == user_from_search_with_data
    assert endpoint.called


async def test__search_user_by_email_post_without_extra_data__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_without_data: UserFromSearch,
    user_from_search_without_data_json: Dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
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
        user = await bot.search_user_by_email_post(
            bot_id=bot_id,
            email="ad_user@cts.com",
        )

    # - Assert -
    assert user == user_from_search_without_data
    assert endpoint.called


async def test__search_user_by_email_post__list_response_is_invalid(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    user_from_search_with_data_json: Dict[str, Any],
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
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
        with pytest.raises(InvalidBotXResponsePayloadError):
            await bot.search_user_by_email_post(
                bot_id=bot_id,
                email="ad_user@cts.com",
            )

    # - Assert -
    assert endpoint.called


async def test__search_user_by_email_post__non_400_status_is_not_retried(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        error_payload("unexpected_error"),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    async with bot_factory() as bot:
        with pytest.raises(InvalidBotXStatusCodeError):
            await bot.search_user_by_email_post(
                bot_id=bot_id,
                email="ad_user@cts.com",
            )

    assert endpoint.called


async def test__search_user_by_email_post__invalid_payload_raises_invalid_response(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    request = BotXRequest(
        method="POST",
        path="/api/v3/botx/users/by_email",
        json={"email": "ad_user@cts.com"},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"foo": "bar"}),
        HTTPStatus.OK,
    )

    async with bot_factory() as bot:
        with pytest.raises(InvalidBotXResponsePayloadError):
            await bot.search_user_by_email_post(
                bot_id=bot_id,
                email="ad_user@cts.com",
            )

    assert endpoint.called
