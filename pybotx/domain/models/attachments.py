import base64
from contextlib import asynccontextmanager
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal
from collections.abc import AsyncGenerator

from aiofiles.tempfile import SpooledTemporaryFile

from pybotx.domain.constants import CHUNK_SIZE
from pybotx.domain.ports.async_buffer import AsyncBufferReadable
from pybotx.domain.models.enums import AttachmentTypes
from pybotx.domain.models.stickers import Sticker


@dataclass(slots=True)
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


@dataclass(slots=True)
class AttachmentImage(FileAttachmentBase):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass(slots=True)
class AttachmentVideo(FileAttachmentBase):
    type: Literal[AttachmentTypes.VIDEO]

    duration: int


@dataclass(slots=True)
class AttachmentDocument(FileAttachmentBase):
    type: Literal[AttachmentTypes.DOCUMENT]


@dataclass(slots=True)
class AttachmentVoice(FileAttachmentBase):
    type: Literal[AttachmentTypes.VOICE]

    duration: int


@dataclass(slots=True)
class Location:
    name: str
    address: str
    latitude: str
    longitude: str


@dataclass(slots=True)
class Contact:
    name: str


@dataclass(slots=True)
class Link:
    url: str
    title: str
    preview: str
    text: str


IncomingFileAttachment = (
    AttachmentImage
    | AttachmentVideo
    | AttachmentDocument
    | AttachmentVoice
)


@dataclass(slots=True)
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


IncomingAttachment = (
    IncomingFileAttachment
    | Location
    | Contact
    | Link
    | Sticker
)


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
