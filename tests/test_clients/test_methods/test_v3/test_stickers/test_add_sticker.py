import uuid

import pytest

from botx.clients.methods.v3.stickers.add_sticker import AddSticker
from botx.concurrency import callable_to_coroutine
from botx.testing.content import PNG_DATA

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_add_sticker_into_sticker_pack(client, requests_client):
    emoji = "🐢"

    method = AddSticker(
        pack_id=uuid.uuid4(),
        emoji=emoji,
        image=PNG_DATA,
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
