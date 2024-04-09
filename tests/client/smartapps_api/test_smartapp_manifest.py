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
            web_default_layout=SmartappManifestWebLayoutChoices.full,
            web_expanded_layout=SmartappManifestWebLayoutChoices.full,
            web_always_pinned=True,
        )

    # - Assert -
    assert endpoint.called
    assert smartapp_manifest == SmartappManifest(
        web=SmartappManifestWebParams(
            default_layout=SmartappManifestWebLayoutChoices.full,
            expanded_layout=SmartappManifestWebLayoutChoices.full,
            always_pinned=True,
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
            "manifest": {
                "web": {
                    "always_pinned": False,
                    "default_layout": "minimal",
                    "expanded_layout": "half",
                },
            },
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
    )
