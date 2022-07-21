from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, HandlerCollector, lifespan_wrapper
from pybotx.models.bot_account import BotAccountWithSecret
from pybotx.models.smartapps import SmartApp

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
        f"https://{host}/api/v3/botx/smartapps/list",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "result": {
                    "phonebook_version": 1,
                    "smartapps": [
                        {
                            "app_id": "amazing_smartapp",
                            "avatar": "https://cts.example.com/uploads/profile_avatar/foo",
                            "avatar_preview": "https://cts.example.com/uploads/profile_avatar/bar",
                            "enabled": True,
                            "id": "dc4acaf2-310f-4b0f-aec7-253b9def42ac",
                            "name": "Amazing SmartApp",
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
        smartapps_list, version = await bot.get_smartapps_list(
            bot_id=bot_id,
        )

    # - Assert -
    assert endpoint.called
    assert smartapps_list == [
        SmartApp(
            app_id="amazing_smartapp",
            avatar="https://cts.example.com/uploads/profile_avatar/foo",
            avatar_preview="https://cts.example.com/uploads/profile_avatar/bar",
            enabled=True,
            id=UUID("dc4acaf2-310f-4b0f-aec7-253b9def42ac"),
            name="Amazing SmartApp",
        ),
    ]
    assert version == 1
