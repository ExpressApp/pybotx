import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.stickers.image_not_valid import ImageNotValidError
from botx.clients.methods.v3.stickers.add_sticker import AddSticker
from botx.concurrency import callable_to_coroutine
from botx.testing.content import PNG_DATA

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_image_not_valid(client, requests_client):
    method = AddSticker(
        host="example.com",
        pack_id=uuid.uuid4(),
        emoji="🐢",
        image=PNG_DATA,
    )

    errors_to_raise = {
        AddSticker: (
            HTTPStatus.BAD_REQUEST,
            {},
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(ImageNotValidError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
