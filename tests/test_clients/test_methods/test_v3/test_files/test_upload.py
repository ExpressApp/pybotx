import uuid

import pytest

from botx.clients.methods.v3.files.upload import UploadFile
from botx.concurrency import callable_to_coroutine
from botx.models.files import File
from botx.testing.content import PNG_DATA

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_upload_file(client, requests_client):
    file_name = "image.png"

    image = File(file_name=file_name, data=PNG_DATA)
    method = UploadFile(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        file=image,
        meta={},
    )

    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)
    meta_file = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert meta_file.file_name == file_name

    assert client.requests[0].file.file_name == file_name
