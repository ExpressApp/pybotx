from uuid import uuid4

import pytest

from botx.clients.methods.v3.files.download import DownloadFile
from botx.clients.methods.v3.files.upload import UploadFile
from botx.models.files import File
from botx.testing.content import PNG_DATA

pytestmark = pytest.mark.asyncio


async def test_upload_file(client, message):
    image = File(file_name="image.png", data=PNG_DATA)
    await client.bot.upload_file(message.credentials, image, group_chat_id=uuid4())

    assert isinstance(client.requests[0], UploadFile)


async def test_download_file(client, message):
    await client.bot.download_file(
        message.credentials,
        file_id=uuid4(),
        group_chat_id=uuid4(),
    )

    assert isinstance(client.requests[0], DownloadFile)


async def test_custom_filename(client, message):
    file = await client.bot.download_file(
        message.credentials,
        file_id=uuid4(),
        group_chat_id=uuid4(),
        file_name="myname",
    )

    assert file.file_name.split(".")[0] == "myname"
