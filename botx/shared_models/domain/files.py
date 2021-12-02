from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Union
from uuid import UUID

from aiofiles.tempfile import SpooledTemporaryFile

from botx.bot.contextvars import bot_id_var, bot_var, chat_id_var
from botx.constants import CHUNK_SIZE
from botx.models.enums import AttachmentTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class AsyncFileBase:
    type: AttachmentTypes
    filename: str
    size: int

    is_async_file: Literal[True]

    _file_id: UUID

    @asynccontextmanager
    async def open(self) -> AsyncGenerator[SpooledTemporaryFile, None]:
        bot = bot_var.get()

        async with SpooledTemporaryFile(max_size=CHUNK_SIZE) as tmp_file:
            await bot.download_file(
                bot_id=bot_id_var.get(),
                chat_id=chat_id_var.get(),
                file_id=self._file_id,
                async_buffer=tmp_file,
            )

            yield tmp_file


@dataclass
class Image(AsyncFileBase):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass
class Video(AsyncFileBase):
    type: Literal[AttachmentTypes.VIDEO]

    duration: int


@dataclass
class Document(AsyncFileBase):
    type: Literal[AttachmentTypes.DOCUMENT]


@dataclass
class Voice(AsyncFileBase):
    type: Literal[AttachmentTypes.VOICE]

    duration: int


File = Union[Image, Video, Document, Voice]
