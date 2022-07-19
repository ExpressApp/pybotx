from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, HandlerCollector, lifespan_wrapper
from pybotx.client.exceptions.users import InvalidProfileDataError
from pybotx.models.attachments import AttachmentImage
from pybotx.models.bot_account import BotAccountWithSecret
from pybotx.models.enums import AttachmentTypes

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
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.put(
        f"https://{host}/api/v3/botx/users/update_profile",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": True,
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
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
    bot_account: BotAccountWithSecret,
    avatar: AttachmentImage,
) -> None:
    # - Arrange -
    endpoint = respx_mock.put(
        f"https://{host}/api/v3/botx/users/update_profile",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "avatar": {
                "data": "data:image/png;base64,SGVsbG8sIHdvcmxkIQ==",
                "file_name": "avatar.png",
            },
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
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": True,
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
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
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.put(
        f"https://{host}/api/v3/botx/users/update_profile",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
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
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "invalid_profile",
                "errors": [],
                "error_data": {
                    "errors": {"field": "invalid"},
                    "error_description": "Invalid profile data",
                    "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
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
