from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Union

from aiofiles.tempfile import SpooledTemporaryFile

from botx.constants import CHUNK_SIZE
from botx.models.enums import AttachmentTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
class AttachmentLocation:
    type: Literal[AttachmentTypes.LOCATION]

    name: str
    address: str
    latitude: str
    longitude: str


@dataclass
class AttachmentContact:
    type: Literal[AttachmentTypes.CONTACT]

    name: str


@dataclass
class AttachmentLink:
    type: Literal[AttachmentTypes.LINK]

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
IncomingAttachment = Union[
    IncomingFileAttachment,
    AttachmentLocation,
    AttachmentContact,
    AttachmentLink,
]
