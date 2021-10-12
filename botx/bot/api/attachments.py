import base64
from typing import Literal, Union, cast

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


class BotAPIAttachmentDocumentData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentDocument(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.DOCUMENT]
    data: BotAPIAttachmentDocumentData


class BotAPIAttachmentImageData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentImage(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.IMAGE]
    data: BotAPIAttachmentImageData


BotAPIAttachment = Union[BotAPIAttachmentImage, BotAPIAttachmentDocument]


def convert_api_attachment_to_domain(
    api_attachment: BotAPIAttachment,
) -> IncomingFile:
    attachment_type = convert_attachment_type_to_domain(api_attachment.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)

        return AttachmentImage(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=0,
            _file_id=None,
            _is_async_file=False,
            _content=decode_rfc2397(api_attachment.data.content),
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)

        return AttachmentDocument(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=0,
            _file_id=None,
            _is_async_file=False,
            _content=decode_rfc2397(api_attachment.data.content),
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")


def decode_rfc2397(encoded_content: str) -> bytes:
    return base64.b64decode(encoded_content.split(",", 1)[1].encode())
