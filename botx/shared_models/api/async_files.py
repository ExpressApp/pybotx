from typing import cast
from uuid import UUID

from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.api.enums import (
    APIAttachmentTypes,
    convert_attachment_type_to_domain,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.domain.attachments import (
    AttachmentDocument,
    AttachmentImage,
    IncomingFile,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class APIAsyncFile(VerifiedPayloadBaseModel):
    type: APIAttachmentTypes
    file_id: UUID
    file_name: str
    file_size: int

    class Config:
        """BotX sends extra fields which are used by client only.

        We skip their validation, but extra fields will be saved during
        serialization/deserialization.
        """

        extra = "allow"


def convert_async_file_to_file_attachment(async_file: APIAsyncFile) -> IncomingFile:
    attachment_type = convert_attachment_type_to_domain(async_file.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)

        return AttachmentImage(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            _file_id=async_file.file_id,
            _is_async_file=True,
            _content=None,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)

        return AttachmentDocument(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            _file_id=async_file.file_id,
            _is_async_file=True,
            _content=None,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")
