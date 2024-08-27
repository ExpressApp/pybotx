from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    SmartappManifest,
    SmartappManifestWebLayoutChoices,
    SmartappManifestWebParams,
    lifespan_wrapper,
)
from pybotx.client.smartapps_api.smartapp_manifest import (
    SmartappManifestUnreadCounterParams,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__send_smartapp_manifest__all_params_provided__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v1/botx/smartapps/manifest",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "manifest": {
                "web": {
                    "always_pinned": True,
                    "default_layout": "full",
                    "expanded_layout": "full",
                },
                "unread_counter_link": {
                    "user_huid": ["e3568b81-0446-4030-9210-1725841bf8f0"],
                    "group_chat_id": ["adc03af8-9193-4d3b-b913-7a023cdb4029"],
                    "app_id": ["test_app"],
                },
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "result": {
                    "web": {
                        "always_pinned": True,
                        "default_layout": "full",
                        "expanded_layout": "full",
                    },
                    "unread_counter_link": {
                        "user_huid": ["e3568b81-0446-4030-9210-1725841bf8f0"],
                        "group_chat_id": ["adc03af8-9193-4d3b-b913-7a023cdb4029"],
                        "app_id": ["test_app"],
                    },
                },
                "status": "ok",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        smartapp_manifest = await bot.send_smartapp_manifest(
            bot_id=bot_id,
            web_layout=SmartappManifestWebParams(
                default_layout=SmartappManifestWebLayoutChoices.full,
                expanded_layout=SmartappManifestWebLayoutChoices.full,
                always_pinned=True,
            ),
            unread_counter=SmartappManifestUnreadCounterParams(
                user_huid=[UUID("e3568b81-0446-4030-9210-1725841bf8f0")],
                group_chat_id=[UUID("adc03af8-9193-4d3b-b913-7a023cdb4029")],
                app_id=["test_app"],
            ),
        )

    # - Assert -
    assert endpoint.called
    assert smartapp_manifest == SmartappManifest(
        web=SmartappManifestWebParams(
            default_layout=SmartappManifestWebLayoutChoices.full,
            expanded_layout=SmartappManifestWebLayoutChoices.full,
            always_pinned=True,
        ),
        unread_counter_link=SmartappManifestUnreadCounterParams(
            user_huid=[UUID("e3568b81-0446-4030-9210-1725841bf8f0")],
            group_chat_id=[UUID("adc03af8-9193-4d3b-b913-7a023cdb4029")],
            app_id=["test_app"],
        ),
    )


async def test__send_smartapp_manifest__only_default_params_provided__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v1/botx/smartapps/manifest",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "manifest": {},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "result": {
                    "web": {
                        "always_pinned": False,
                        "default_layout": "minimal",
                        "expanded_layout": "half",
                    },
                    "unread_counter_link": {
                        "app_id": [],
                        "group_chat_id": [],
                        "user_huid": [],
                    },
                },
                "status": "ok",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        smartapp_manifest = await bot.send_smartapp_manifest(bot_id=bot_id)

    # - Assert -
    assert endpoint.called
    assert smartapp_manifest == SmartappManifest(
        web=SmartappManifestWebParams(
            default_layout=SmartappManifestWebLayoutChoices.minimal,
            expanded_layout=SmartappManifestWebLayoutChoices.half,
            always_pinned=False,
        ),
        unread_counter_link=SmartappManifestUnreadCounterParams(
            user_huid=[],
            group_chat_id=[],
            app_id=[],
        ),
    )
