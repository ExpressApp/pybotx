from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, lifespan_wrapper
from botx.models.stickers import StickerPackFromList


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__iterate_by_sticker_packs__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/stickers/packs",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "d881f83a-db30-4cff-b60e-f24ac53deecf"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "packs": [
                        {
                            "id": "26080153-a57d-5a8c-af0e-fdecee3c4435",
                            "name": "Sticker Pack",
                            "preview": "https://cts-host/uploads/sticker_pack/26080153-a57d-5a8c-af0e-fdecee3c4435/9df3143975ad4e6d93bf85079fbb5f1d.png?v=1614781425296",
                            "public": True,
                            "stickers_count": 2,
                            "stickers_order": [
                                "a998f599-d7ac-5e04-9fdb-2d98224ce4ff",
                                "25054ac4-8be2-5a4b-ae00-9efd38c73fb7",
                            ],
                            "inserted_at": "2020-11-28T12:56:43.672163Z",
                            "updated_at": "2021-02-18T12:52:31.571133Z",
                            "deleted_at": None,
                        },
                    ],
                    "pagination": {
                        "after": None,
                    },
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
    sticker_pack_list = []
    async with lifespan_wrapper(built_bot) as bot:
        sticker_pack_pages = bot.iterate_by_sticker_packs(
            bot_id=bot_id,
            user_huid=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        )
        async for sticker_packs in sticker_pack_pages:
            sticker_pack_list.append(sticker_packs)

    # - Assert -
    assert sticker_pack_list == [
        StickerPackFromList(
            id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
            name="Sticker Pack",
            is_public=True,
            stickers_count=2,
            stickers_order=[
                UUID("a998f599-d7ac-5e04-9fdb-2d98224ce4ff"),
                UUID("25054ac4-8be2-5a4b-ae00-9efd38c73fb7"),
            ],
        ),
    ]

    assert endpoint.called
