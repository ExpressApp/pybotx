import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.stickers.sticker_pack_or_sticker_not_found import (
    StickerPackOrStickerNotFoundData,
    StickerPackOrStickerNotFoundError,
)
from botx.clients.methods.v3.stickers.sticker import GetSticker
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_sticker_not_found(client, requests_client):
    method = GetSticker(
        host="example.com",
        pack_id=uuid.uuid4(),
        sticker_id=uuid.uuid4(),
    )

    errors_to_raise = {
        GetSticker: (
            HTTPStatus.NOT_FOUND,
            StickerPackOrStickerNotFoundData(
                pack_id=method.pack_id,
                sticker_id=method.sticker_id,
            ),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(StickerPackOrStickerNotFoundError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
