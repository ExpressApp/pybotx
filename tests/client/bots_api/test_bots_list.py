from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper
from pybotx.models.bot_catalog import BotsListItem

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__smartapps_list__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v1/botx/bots/catalog",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "result": {
                    "generated_at": datetime(2023, 1, 1).isoformat(),
                    "bots": [
                        {
                            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                            "name": "First bot",
                            "description": "My bot",
                            "avatar": None,
                            "enabled": True,
                        },
                        {
                            "user_huid": "66d74e0a-b3c8-4c28-a03f-baf2d1d3f4c7",
                            "name": "Second bot",
                            "description": "Your bot",
                            "avatar": "https://cts.example.com/uploads/profile_avatar/bar",
                            "enabled": True,
                        },
                    ],
                },
                "status": "ok",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bots_list, timestamp = await bot.get_bots_list(
            bot_id=bot_id,
            since=datetime(2022, 1, 1),
        )

    # - Assert -
    assert endpoint.called
    assert timestamp == datetime(2023, 1, 1)
    assert bots_list == [
        BotsListItem(
            id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
            name="First bot",
            description="My bot",
            avatar=None,
            enabled=True,
        ),
        BotsListItem(
            id=UUID("66d74e0a-b3c8-4c28-a03f-baf2d1d3f4c7"),
            name="Second bot",
            description="Your bot",
            avatar="https://cts.example.com/uploads/profile_avatar/bar",
            enabled=True,
        ),
    ]
