from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    StickerPackOrStickerNotFoundError,
    lifespan_wrapper,
)
from botx.models.stickers import Sticker, StickerPack


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__get_sticker__sticker_pack_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.get_sticker_pack(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
            )

    # - Assert -
    assert "pack_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__get_sticker_pack__stickers_in_right_order_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/stickers/packs/d881f83a-db30-4cff-b60e-f24ac53deecf",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "d881f83a-db30-4cff-b60e-f24ac53deecf",
                    "name": "Sticker Pack",
                    "public": True,
                    "preview": "https://cts-host/uploads/sticker_pack/image.png",
                    "stickers_order": [
                        "528c3953-5842-5a30-b2cb-8a09218497bc",
                        "750bb400-bb37-4ff9-aa92-cc293f09cafa",
                    ],
                    "stickers": [
                        {
                            "id": "750bb400-bb37-4ff9-aa92-cc293f09cafa",
                            "emoji": "🤔",
                            "link": "https://cts-host/uploads/sticker_pack/image.png",
                            "inserted_at": "2020-12-28T12:56:43.672163Z",
                            "updated_at": "2020-12-28T12:56:43.672163Z",
                            "deleted_at": None,
                        },
                        {
                            "id": "528c3953-5842-5a30-b2cb-8a09218497bc",
                            "emoji": "🤔",
                            "link": "https://cts-host/uploads/sticker_pack/image.png",
                            "inserted_at": "2020-12-28T12:56:43.672163Z",
                            "updated_at": "2020-12-28T12:56:43.672163Z",
                            "deleted_at": None,
                        },
                    ],
                    "inserted_at": "2020-12-28T12:56:43.672163Z",
                    "updated_at": "2020-12-28T12:56:43.672163Z",
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
        sticker_pack = await bot.get_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        )

    # - Assert -
    assert sticker_pack == StickerPack(
        id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        name="Sticker Pack",
        is_public=True,
        stickers=[
            Sticker(
                id=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
                emoji="🤔",
                image_link="https://cts-host/uploads/sticker_pack/image.png",
            ),
            Sticker(
                id=UUID("750bb400-bb37-4ff9-aa92-cc293f09cafa"),
                emoji="🤔",
                image_link="https://cts-host/uploads/sticker_pack/image.png",
            ),
        ],
    )

    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__get_sticker_pack__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/stickers/packs/d881f83a-db30-4cff-b60e-f24ac53deecf",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "d881f83a-db30-4cff-b60e-f24ac53deecf",
                    "name": "Sticker Pack",
                    "public": True,
                    "preview": "https://cts-host/uploads/sticker_pack/image.png",
                    "stickers_order": [],
                    "stickers": [
                        {
                            "id": "528c3953-5842-5a30-b2cb-8a09218497bc",
                            "emoji": "🤔",
                            "link": "https://cts-host/uploads/sticker_pack/image.png",
                            "inserted_at": "2020-12-28T12:56:43.672163Z",
                            "updated_at": "2020-12-28T12:56:43.672163Z",
                            "deleted_at": None,
                        },
                    ],
                    "inserted_at": "2020-12-28T12:56:43.672163Z",
                    "updated_at": "2020-12-28T12:56:43.672163Z",
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
        sticker_pack = await bot.get_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        )

    # - Assert -
    assert sticker_pack == StickerPack(
        id=UUID("d881f83a-db30-4cff-b60e-f24ac53deecf"),
        name="Sticker Pack",
        is_public=True,
        stickers=[
            Sticker(
                id=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
                emoji="🤔",
                image_link="https://cts-host/uploads/sticker_pack/image.png",
            ),
        ],
    )

    assert endpoint.called
