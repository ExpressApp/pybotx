import uuid

import pytest

from botx.clients.methods.v3.files.download import DownloadFile
from botx.concurrency import callable_to_coroutine
from botx.models.files import File

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_download_file(client, requests_client):
    file_id = uuid.uuid4()
    method = DownloadFile(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        file_id=file_id,
        is_preview=False,
    )

    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)
    file = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert isinstance(file, File)

    assert client.requests[0].file_id == file_id
