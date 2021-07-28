"""Module with attachments meta for botx."""

from typing import Optional, Union

from pydantic import Field

from botx.models.base import BotXBaseModel
from botx.models.enums import AttachmentsTypes

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401


class FileAttachmentMeta(BotXBaseModel):
    """Common metadata of file."""

    #: type of attachment
    type: str

    #: name of file.
    file_name: str

    #: mime type of file
    file_mime_type: Optional[str]

    #: file preview in RFC 2397 format.
    file_preview_base64: Optional[str]


class ImageAttachmentMeta(FileAttachmentMeta):
    """BotX API image attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.image] = Field(default=AttachmentsTypes.image)


class VideoAttachmentMeta(FileAttachmentMeta):
    """BotX API video attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.video] = Field(default=AttachmentsTypes.video)


class DocumentAttachmentMeta(FileAttachmentMeta):
    """BotX API document attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.document] = Field(default=AttachmentsTypes.document)


class VoiceAttachmentMeta(FileAttachmentMeta):
    """BotX API voice attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.voice] = Field(default=AttachmentsTypes.voice)


class ContactAttachmentMeta(BotXBaseModel):
    """BotX API contact attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.contact] = Field(default=AttachmentsTypes.contact)

    #: name of contact
    contact_name: str


class LocationAttachmentMeta(BotXBaseModel):
    """BotX API location attachment meta container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.location] = Field(default=AttachmentsTypes.location)

    #: address of location
    location_address: str


AttachmentMeta = Union[
    ImageAttachmentMeta,
    VideoAttachmentMeta,
    DocumentAttachmentMeta,
    VoiceAttachmentMeta,
    ContactAttachmentMeta,
    LocationAttachmentMeta,
]
