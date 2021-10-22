from typing import Optional, cast
from uuid import UUID

from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.api.enums import (
    APIAttachmentTypes,
    convert_attachment_type_to_domain,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.domain.files import Document, File, Image, Video, Voice

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class APIAsyncFile(VerifiedPayloadBaseModel):
    type: APIAttachmentTypes
    file_id: UUID
    file_name: str
    file_size: int
    duration: Optional[int] = None

    class Config:
        """BotX sends extra fields which are used by client only.

        We skip their validation, but extra fields will be saved during
        serialization/deserialization.
        """

        extra = "allow"


def convert_async_file_to_file(async_file: APIAsyncFile) -> File:
    attachment_type = convert_attachment_type_to_domain(async_file.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)

        return Image(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.VIDEO:
        attachment_type = cast(Literal[AttachmentTypes.VIDEO], attachment_type)
        assert async_file.duration is not None

        return Video(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)

        return Document(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.VOICE:
        attachment_type = cast(Literal[AttachmentTypes.VOICE], attachment_type)
        assert async_file.duration is not None

        return Voice(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")
