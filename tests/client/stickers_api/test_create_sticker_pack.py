from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    StickerPack,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__create_sticker_pack__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs",
        headers={"Authorization": "Bearer token"},
        json={"name": "Sticker Pack", "user_huid": "d881f83a-db30-4cff-b60e-f24ac53deecf"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "26080153-a57d-5a8c-af0e-fdecee3c4435",
                    "name": "Sticker Pack",
                    "public": False,
                    "preview": None,
                    "stickers": [],
                    "stickers_order": [],
                    "inserted_at": "2021-07-10T00:27:55.616703Z",
                    "updated_at": "2021-07-10T00:27:55.616703Z",
                    "deleted_at": None,
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sticker_pack = await bot.create_sticker_pack(
            bot_id=bot_id,
            name="Sticker Pack",
            huid=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        )

    # - Assert -
    assert sticker_pack == StickerPack(
        id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
        name="Sticker Pack",
        is_public=False,
        stickers=[],
    )

    assert endpoint.called
