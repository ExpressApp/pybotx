from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, StickerPack, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__create_sticker_pack__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/stickers/packs",
        headers={"Authorization": "Bearer token"},
        json={"name": "Sticker Pack"},
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sticker_pack = await bot.create_sticker_pack(bot_id=bot_id, name="Sticker Pack")

    # - Assert -
    assert sticker_pack == StickerPack(
        id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
        name="Sticker Pack",
        is_public=False,
        stickers_order=[],
        stickers=[],
    )

    assert endpoint.called
