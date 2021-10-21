from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.domain.files import Image


@respx.mock
@pytest.mark.asyncio
async def test__attachment__open(
    chat_id: UUID,
    host: str,
    set_contexvars: None,
) -> None:
    # - Arrange -
    file_id = UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80")

    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": chat_id,
            "file_id": file_id,
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content=b"Hello, world!\n",
        ),
    )

    attachment = Image(
        type=AttachmentTypes.IMAGE,
        filename="test.png",
        size=10,
        _file_id=file_id,
    )

    # - Act -
    async with attachment.open() as fo:
        read_content = await fo.read()

    # - Assert -
    assert endpoint.called
    assert read_content == b"Hello, world!\n"
