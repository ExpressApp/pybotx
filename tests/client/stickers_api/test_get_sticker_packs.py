from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper
from pybotx.models.stickers import StickerPackFromList

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__iterate_by_sticker_packs__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
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
                            "preview": "https://cts-host/uploads/sticker_pack/image.png",
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
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])
    sticker_pack_list = []

    # - Act -
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
            sticker_ids=[
                UUID("a998f599-d7ac-5e04-9fdb-2d98224ce4ff"),
                UUID("25054ac4-8be2-5a4b-ae00-9efd38c73fb7"),
            ],
        ),
    ]
    assert endpoint.called


async def test__iterate_by_sticker_packs__iterate_by_pages_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    monkeypatch.setattr("pybotx.bot.bot.STICKER_PACKS_PER_PAGE", 2)

    # Mock order matters
    # https://lundberg.github.io/respx/guide/#routing-requests
    second_sticker_endpoint_call = respx_mock.get(
        f"https://{host}/api/v3/botx/stickers/packs",
        headers={"Authorization": "Bearer token"},
        params={
            "user_huid": "d881f83a-db30-4cff-b60e-f24ac53deecf",
            "limit": 2,
            "after": "base64string",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "packs": [
                        {
                            "id": "750bb400-bb37-4ff9-aa92-cc293f09cafa",
                            "name": "Sticker Pack 3",
                            "preview": "https://cts-host/uploads/sticker_pack/image.png",
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
    first_sticker_endpoint_call = respx_mock.get(
        f"https://{host}/api/v3/botx/stickers/packs",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "d881f83a-db30-4cff-b60e-f24ac53deecf", "limit": 2},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "packs": [
                        {
                            "id": "26080153-a57d-5a8c-af0e-fdecee3c4435",
                            "name": "Sticker Pack 1",
                            "preview": "https://cts-host/uploads/sticker_pack/image.png",
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
                        {
                            "id": "89152263-2484-4e00-bc6c-90003027e39e",
                            "name": "Sticker Pack 2",
                            "preview": "https://cts-host/uploads/sticker_pack/image.png",
                            "public": True,
                            "stickers_count": 1,
                            "stickers_order": [
                                "a998f599-d7ac-5e04-9fdb-2d98224ce4ff",
                            ],
                            "inserted_at": "2020-11-28T12:56:43.672163Z",
                            "updated_at": "2021-02-18T12:52:31.571133Z",
                            "deleted_at": None,
                        },
                    ],
                    "pagination": {
                        "after": "base64string",
                    },
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    sticker_pack_list = []

    # - Act -
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
            name="Sticker Pack 1",
            is_public=True,
            stickers_count=2,
            sticker_ids=[
                UUID("a998f599-d7ac-5e04-9fdb-2d98224ce4ff"),
                UUID("25054ac4-8be2-5a4b-ae00-9efd38c73fb7"),
            ],
        ),
        StickerPackFromList(
            id=UUID("89152263-2484-4e00-bc6c-90003027e39e"),
            name="Sticker Pack 2",
            is_public=True,
            stickers_count=1,
            sticker_ids=[
                UUID("a998f599-d7ac-5e04-9fdb-2d98224ce4ff"),
            ],
        ),
        StickerPackFromList(
            id=UUID("750bb400-bb37-4ff9-aa92-cc293f09cafa"),
            name="Sticker Pack 3",
            is_public=True,
            stickers_count=2,
            sticker_ids=[
                UUID("a998f599-d7ac-5e04-9fdb-2d98224ce4ff"),
                UUID("25054ac4-8be2-5a4b-ae00-9efd38c73fb7"),
            ],
        ),
    ]
    assert first_sticker_endpoint_call.called
    assert second_sticker_endpoint_call.called
