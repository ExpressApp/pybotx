import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.sticker_pack_not_found import (
    StickerPackNotFoundData,
    StickerPackNotFoundError,
)
from botx.clients.methods.v3.stickers.sticker_pack import GetStickerPack
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_sticker_pack_not_found(client, requests_client):
    method = GetStickerPack(
        host="example.com",
        pack_id=uuid.uuid4(),
    )

    errors_to_raise = {
        GetStickerPack: (
            HTTPStatus.NOT_FOUND,
            StickerPackNotFoundData(pack_id=method.pack_id),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(StickerPackNotFoundError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
