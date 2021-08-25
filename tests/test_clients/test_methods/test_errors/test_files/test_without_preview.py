import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.files.without_preview import (
    WithoutPreviewData,
    WithoutPreviewError,
)
from botx.clients.methods.v3.files.download import DownloadFile
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_without_preview(client, requests_client):
    method = DownloadFile(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        file_id=uuid.uuid4(),
        is_preview=True,
    )

    errors_to_raise = {
        DownloadFile: (
            HTTPStatus.BAD_REQUEST,
            WithoutPreviewData(
                file_id=method.file_id,
                group_chat_id=method.group_chat_id,
                error_description="test",
            ),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(WithoutPreviewError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
