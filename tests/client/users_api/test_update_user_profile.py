from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx.infrastructure.client.exceptions.users import InvalidProfileDataError
from pybotx.domain.models.attachments import AttachmentImage
from pybotx.domain.models.enums import AttachmentTypes
from pybotx.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


@pytest.fixture
def avatar() -> AttachmentImage:
    return AttachmentImage(
        type=AttachmentTypes.IMAGE,
        filename="avatar.png",
        size=len(b"Hello, world!"),
        is_async_file=False,
        content=b"Hello, world!",
    )


async def test__update_user_profile__minimal_update_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="PUT",
        path="/api/v3/botx/users/update_profile",
        json={
            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload(True),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        await bot.update_user_profile(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    assert endpoint.called


async def test__update_user_profile__maximum_update_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    avatar: AttachmentImage,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="PUT",
        path="/api/v3/botx/users/update_profile",
        json={
            "avatar": "data:image/png;base64,SGVsbG8sIHdvcmxkIQ==",
            "company": "Doge Co",
            "company_position": "Chief",
            "department": "Commercy",
            "description": "Just boss",
            "manager": "Bob",
            "name": "John Bork",
            "office": "Moscow",
            "public_name": "Johny B.",
            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload(True),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        await bot.update_user_profile(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
            avatar=avatar,
            name="John Bork",
            public_name="Johny B.",
            company="Doge Co",
            company_position="Chief",
            description="Just boss",
            department="Commercy",
            office="Moscow",
            manager="Bob",
        )

    # - Assert -
    assert endpoint.called


async def test__update_user_profile__invalid_profile_data_error(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="PUT",
        path="/api/v3/botx/users/update_profile",
        json={
            "company": "Doge Co",
            "company_position": "Chief",
            "department": "Commercy",
            "description": "Just boss",
            "manager": "Bob",
            "name": "John Bork",
            "office": "Moscow",
            "public_name": "Johny B.",
            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        error_payload(
            "invalid_profile",
            error_data={
                "errors": {"field": "invalid"},
                "error_description": "Invalid profile data",
                "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
            },
        ),
        HTTPStatus.BAD_REQUEST,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(InvalidProfileDataError):
            await bot.update_user_profile(
                bot_id=bot_id,
                user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                name="John Bork",
                public_name="Johny B.",
                company="Doge Co",
                company_position="Chief",
                description="Just boss",
                department="Commercy",
                office="Moscow",
                manager="Bob",
            )

    # - Assert -
    assert endpoint.called
