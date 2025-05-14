import base64
from contextlib import asynccontextmanager
from dataclasses import dataclass
from types import MappingProxyType
from typing import AsyncGenerator, Literal, Union, cast
from uuid import UUID

from aiofiles.tempfile import SpooledTemporaryFile

from pybotx.async_buffer import AsyncBufferReadable
from pybotx.constants import CHUNK_SIZE
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APIAttachmentTypes,
    AttachmentTypes,
    convert_attachment_type_to_domain,
)
from pybotx.models.stickers import Sticker


@dataclass
class FileAttachmentBase:
    type: AttachmentTypes
    filename: str
    size: int

    is_async_file: Literal[False]

    content: bytes

    @asynccontextmanager
    async def open(self) -> AsyncGenerator[SpooledTemporaryFile, None]:
        async with SpooledTemporaryFile(max_size=CHUNK_SIZE) as tmp_file:
            await tmp_file.write(self.content)
            await tmp_file.seek(0)

            yield tmp_file


@dataclass
class AttachmentImage(FileAttachmentBase):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass
class AttachmentVideo(FileAttachmentBase):
    type: Literal[AttachmentTypes.VIDEO]

    duration: int


@dataclass
class AttachmentDocument(FileAttachmentBase):
    type: Literal[AttachmentTypes.DOCUMENT]


@dataclass
class AttachmentVoice(FileAttachmentBase):
    type: Literal[AttachmentTypes.VOICE]

    duration: int


@dataclass
class Location:
    name: str
    address: str
    latitude: str
    longitude: str


@dataclass
class Contact:
    name: str


@dataclass
class Link:
    url: str
    title: str
    preview: str
    text: str


IncomingFileAttachment = Union[
    AttachmentImage,
    AttachmentVideo,
    AttachmentDocument,
    AttachmentVoice,
]


@dataclass
class OutgoingAttachment:
    content: bytes
    filename: str
    is_async_file: Literal[False] = False

    @classmethod
    async def from_async_buffer(
        cls,
        async_buffer: AsyncBufferReadable,
        filename: str,
    ) -> "OutgoingAttachment":
        return cls(
            content=await async_buffer.read(),
            filename=filename,
        )


class BotAPIAttachmentImageData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentImage(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.IMAGE]
    data: BotAPIAttachmentImageData


class BotAPIAttachmentVideoData(VerifiedPayloadBaseModel):
    content: str
    file_name: str
    duration: int


class BotAPIAttachmentVideo(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.VIDEO]
    data: BotAPIAttachmentVideoData


class BotAPIAttachmentDocumentData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentDocument(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.DOCUMENT]
    data: BotAPIAttachmentDocumentData


class BotAPIAttachmentVoiceData(VerifiedPayloadBaseModel):
    content: str
    duration: int


class BotAPIAttachmentVoice(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.VOICE]
    data: BotAPIAttachmentVoiceData


class BotAPIAttachmentLocationData(VerifiedPayloadBaseModel):
    location_name: str
    location_address: str
    location_lat: str
    location_lng: str


class BotAPIAttachmentLocation(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LOCATION]
    data: BotAPIAttachmentLocationData


class BotAPIAttachmentContactData(VerifiedPayloadBaseModel):
    contact_name: str


class BotAPIAttachmentContact(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.CONTACT]
    data: BotAPIAttachmentContactData


class BotAPIAttachmentStickerData(VerifiedPayloadBaseModel):
    id: UUID
    link: str
    pack: UUID


class BotAPIAttachmentSticker(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.STICKER]
    data: BotAPIAttachmentStickerData


class BotAPIAttachmentLinkData(VerifiedPayloadBaseModel):
    url: str
    url_title: str
    url_preview: str
    url_text: str


class BotAPIAttachmentLink(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LINK]
    data: BotAPIAttachmentLinkData


BotAPIAttachment = Union[
    BotAPIAttachmentVideo,
    BotAPIAttachmentImage,
    BotAPIAttachmentDocument,
    BotAPIAttachmentVoice,
    BotAPIAttachmentLocation,
    BotAPIAttachmentContact,
    BotAPIAttachmentLink,
    BotAPIAttachmentSticker,
]

IncomingAttachment = Union[
    IncomingFileAttachment,
    Location,
    Contact,
    Link,
    Sticker,
]


def convert_api_attachment_to_domain(  # noqa: WPS212
    api_attachment: BotAPIAttachment,
    message_body: str,
) -> IncomingAttachment:
    attachment_type = convert_attachment_type_to_domain(api_attachment.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)
        api_attachment = cast(BotAPIAttachmentImage, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentImage(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            is_async_file=False,
            content=content,
        )

    if attachment_type == AttachmentTypes.VIDEO:
        attachment_type = cast(Literal[AttachmentTypes.VIDEO], attachment_type)
        api_attachment = cast(BotAPIAttachmentVideo, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentVideo(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            is_async_file=False,
            content=content,
            duration=api_attachment.data.duration,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)
        api_attachment = cast(BotAPIAttachmentDocument, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentDocument(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            is_async_file=False,
            content=content,
        )

    if attachment_type == AttachmentTypes.VOICE:
        attachment_type = cast(Literal[AttachmentTypes.VOICE], attachment_type)
        api_attachment = cast(BotAPIAttachmentVoice, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)
        attachment_extension = get_attachment_extension_from_encoded_content(
            api_attachment.data.content,
        )

        return AttachmentVoice(
            type=attachment_type,
            filename=f"record.{attachment_extension}",
            size=len(content),
            is_async_file=False,
            content=content,
            duration=api_attachment.data.duration,
        )

    if attachment_type == AttachmentTypes.LOCATION:
        attachment_type = cast(Literal[AttachmentTypes.LOCATION], attachment_type)
        api_attachment = cast(BotAPIAttachmentLocation, api_attachment)

        return Location(
            name=api_attachment.data.location_name,
            address=api_attachment.data.location_address,
            latitude=api_attachment.data.location_lat,
            longitude=api_attachment.data.location_lng,
        )

    if attachment_type == AttachmentTypes.CONTACT:
        attachment_type = cast(Literal[AttachmentTypes.CONTACT], attachment_type)
        api_attachment = cast(BotAPIAttachmentContact, api_attachment)

        return Contact(
            name=api_attachment.data.contact_name,
        )

    if attachment_type == AttachmentTypes.LINK:
        attachment_type = cast(Literal[AttachmentTypes.LINK], attachment_type)
        api_attachment = cast(BotAPIAttachmentLink, api_attachment)

        return Link(
            url=api_attachment.data.url,
            title=api_attachment.data.url_title,
            preview=api_attachment.data.url_preview,
            text=api_attachment.data.url_text,
        )

    if attachment_type == AttachmentTypes.STICKER:
        attachment_type = cast(Literal[AttachmentTypes.STICKER], attachment_type)
        api_attachment = cast(BotAPIAttachmentSticker, api_attachment)

        return Sticker(
            id=api_attachment.data.id,
            image_link=api_attachment.data.link,
            pack_id=api_attachment.data.pack,
            emoji=message_body,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")


def get_attachment_extension_from_encoded_content(
    encoded_content: str,
) -> str:
    return encoded_content.split(";")[0].split("/")[1]


def decode_rfc2397(encoded_content: str) -> bytes:
    # "data:image/gif;base64,aGVsbG8=" -> b"hello"
    if not encoded_content:
        return b""

    return base64.b64decode(encoded_content.split(",", 1)[1].encode())


EXTENSIONS_TO_MIMETYPES = MappingProxyType(
    {
        # application
        "7z": "application/x-7z-compressed",
        "abw": "application/x-abiword",
        "ai": "application/postscript",
        "arc": "application/x-freearc",
        "azw": "application/vnd.amazon.ebook",
        "bin": "application/octet-stream",
        "bz": "application/x-bzip",
        "bz2": "application/x-bzip2",
        "cda": "application/x-cdf",
        "csh": "application/x-csh",
        "doc": "application/msword",
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        "eot": "application/vnd.ms-fontobject",
        "eps": "application/postscript",
        "epub": "application/epub+zip",
        "gz": "application/gzip",
        "jar": "application/java-archive",
        "json-api": "application/vnd.api+json",
        "json-patch": "application/json-patch+json",
        "json": "application/json",
        "jsonld": "application/ld+json",
        "mdb": "application/x-msaccess",
        "mpkg": "application/vnd.apple.installer+xml",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "odt": "application/vnd.oasis.opendocument.text",
        "ogx": "application/ogg",
        "pdf": "application/pdf",
        "php": "application/x-httpd-php",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        "ps": "application/postscript",
        "rar": "application/vnd.rar",
        "rtf": "application/rtf",
        "sh": "application/x-sh",
        "swf": "application/x-shockwave-flash",
        "tar": "application/x-tar",
        "vsd": "application/vnd.visio",
        "wasm": "application/wasm",
        "webmanifest": "application/manifest+json",
        "xhtml": "application/xhtml+xml",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xul": "application/vnd.mozilla.xul+xml",
        "zip": "application/zip",
        # audio
        "aac": "audio/aac",
        "mid": "audio/midi",
        "midi": "audio/midi",
        "mp3": "audio/mpeg",
        "oga": "audio/ogg",
        "opus": "audio/opus",
        "wav": "audio/wav",
        "weba": "audio/webm",
        # font
        "otf": "font/otf",
        "ttf": "font/ttf",
        "woff": "font/woff",
        "woff2": "font/woff2",
        # image
        "avif": "image/avif",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "ico": "image/vnd.microsoft.icon",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "svg": "image/svg+xml",
        "svgz": "image/svg+xml",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "webp": "image/webp",
        # text
        "css": "text/css",
        "csv": "text/csv",
        "htm": "text/html",
        "html": "text/html",
        "ics": "text/calendar",
        "js": "text/javascript",
        "mjs": "text/javascript",
        "txt": "text/plain",
        "text": "text/plain",
        "xml": "text/xml",
        # video
        "3g2": "video/3gpp2",
        "3gp": "video/3gpp",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "mp4": "video/mp4",
        "mpeg": "video/mpeg",
        "mpg": "video/mpeg",
        "ogv": "video/ogg",
        "ts": "video/mp2t",
        "webm": "video/webm",
        "wmv": "video/x-ms-wmv",
    },
)
DEFAULT_MIMETYPE = "application/octet-stream"


def encode_rfc2397(content: bytes, mimetype: str) -> str:
    b64_content = base64.b64encode(content).decode()
    return f"data:{mimetype};base64,{b64_content}"


class BotXAPIAttachment(UnverifiedPayloadBaseModel):
    file_name: str
    data: str

    @classmethod
    def from_file_attachment(
        cls,
        attachment: Union[IncomingFileAttachment, OutgoingAttachment],
    ) -> "BotXAPIAttachment":
        assert attachment.content is not None

        mimetype = EXTENSIONS_TO_MIMETYPES.get(
            attachment.filename.split(".")[-1],
            DEFAULT_MIMETYPE,
        )

        return cls(
            file_name=attachment.filename,
            data=encode_rfc2397(attachment.content, mimetype),
        )
