import uuid

import pytest

from botx.clients.methods.v3.stickers.delete_sticker import DeleteSticker
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_delete_sticker(client, requests_client):

    method = DeleteSticker(
        pack_id=uuid.uuid4(),
        sticker_id=uuid.uuid4(),
        host="example.com",
    )
    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)

    result = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert result == "sticker_deleted"
