import pytest

from botx.clients.methods.v3.stickers.sticker_pack_list import GetStickerPackList
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_get_sticker_pack_list(client, requests_client):
    sticker_pack_name = "Test sticker pack"

    method = GetStickerPackList(host="example.com")
    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)

    sticker_pack_list = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert sticker_pack_list.packs[0].name == sticker_pack_name
