import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.files.file_deleted import (
    FileDeletedError,
    FileDeletedErrorData,
)
from botx.clients.methods.v3.files.download import DownloadFile
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_file_deleted(client, requests_client):
    method = DownloadFile(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        file_id=uuid.uuid4(),
        is_preview=False,
    )

    errors_to_raise = {
        DownloadFile: (
            HTTPStatus.NO_CONTENT,
            FileDeletedErrorData(link="/path/to/file", error_description="test"),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(FileDeletedError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
