import uuid

import pytest

from botx.clients.methods.v3.stickers.sticker import GetSticker
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_get_sticker_from_sticker_pack(client, requests_client):
    emoji = "🐢"

    method = GetSticker(
        pack_id=uuid.uuid4(),
        sticker_id=uuid.uuid4(),
        host="example.com",
    )
    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)

    sticker = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert sticker.emoji == emoji
