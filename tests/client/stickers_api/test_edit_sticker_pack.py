from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    StickerPackOrStickerNotFoundError,
    lifespan_wrapper,
)
from pybotx.models.stickers import Sticker, StickerPack

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__edit_sticker_pack__sticker_pack_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.put(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "error_data": {"pack_id": "26080153-a57d-5a8c-af0e-fdecee3c4435"},
                "errors": ["Sticker pack not found."],
                "reason": "pack_not_found",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.edit_sticker_pack(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                name="Sticker Pack 2.0",
                preview=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
                stickers_order=[
                    UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
                    UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
                ],
            )

    # - Assert -
    assert "pack_not_found" in str(exc.value)
    assert endpoint.called


async def test__edit_sticker__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.put(
        f"https://{host}/api/v3/botx/stickers/packs/d881f83a-db30-4cff-b60e-f24ac53deecf",
        headers={"Authorization": "Bearer token"},
        json={
            "name": "Sticker Pack 2.0",
            "preview": "528c3953-5842-5a30-b2cb-8a09218497bc",
            "stickers_order": [
                "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                "528c3953-5842-5a30-b2cb-8a09218497bc",
            ],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "d881f83a-db30-4cff-b60e-f24ac53deecf",
                    "name": "Sticker Pack 2.0",
                    "public": True,
                    "preview": "528c3953-5842-5a30-b2cb-8a09218497bc",
                    "stickers_order": [
                        "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                        "528c3953-5842-5a30-b2cb-8a09218497bc",
                    ],
                    "stickers": [
                        {
                            "id": "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                            "emoji": "🤔",
                            "link": "https://cts-host/uploads/sticker_pack/image.png",
                            "inserted_at": "2020-12-28T12:56:43.672163Z",
                            "updated_at": "2020-12-28T12:56:43.672163Z",
                            "deleted_at": None,
                        },
                        {
                            "id": "528c3953-5842-5a30-b2cb-8a09218497bc",
                            "emoji": "😀",
                            "link": "https://cts-host/uploads/sticker_pack/image.png",
                            "inserted_at": "2020-12-28T12:56:43.672163Z",
                            "updated_at": "2020-12-28T12:56:43.672163Z",
                            "deleted_at": None,
                        },
                    ],
                    "inserted_at": "2020-12-28T12:56:43.672163Z",
                    "updated_at": "2021-07-22T13:26:41.562143Z",
                    "deleted_at": None,
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sticker_pack = await bot.edit_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
            name="Sticker Pack 2.0",
            preview=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
            stickers_order=[
                UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
                UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
            ],
        )

    # - Assert -
    assert sticker_pack == StickerPack(
        id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        name="Sticker Pack 2.0",
        is_public=True,
        stickers=[
            Sticker(
                id=UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
                emoji="🤔",
                image_link="https://cts-host/uploads/sticker_pack/image.png",
            ),
            Sticker(
                id=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
                emoji="😀",
                image_link="https://cts-host/uploads/sticker_pack/image.png",
            ),
        ],
    )

    assert endpoint.called
