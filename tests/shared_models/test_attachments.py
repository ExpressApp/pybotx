import pytest

from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.domain.attachments import AttachmentImage


@pytest.mark.asyncio
async def test__attachment__open() -> None:
    # - Arrange -
    content = b"test"

    attachment = AttachmentImage(
        type=AttachmentTypes.IMAGE,
        filename="test.png",
        content=content,
        is_async_file=False,
        size=len(content),
    )

    # - Act -
    async with attachment.open() as fo:
        read_content = await fo.read()

    # - Assert -
    assert read_content == content
