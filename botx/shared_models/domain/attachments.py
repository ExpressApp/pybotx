from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Union
from uuid import UUID

from aiofiles.tempfile import NamedTemporaryFile

from botx.bot.contextvars import bot_id_var, bot_var, chat_id_var
from botx.bot.models.commands.enums import AttachmentTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class BaseFileAttachment:
    filename: str
    size: int

    _file_id: Optional[UUID]
    _is_async_file: bool
    _content: Optional[bytes]

    @asynccontextmanager  # TODO: SpooledTemporaryFile
    async def open(self) -> AsyncGenerator[NamedTemporaryFile, None]:
        if self._is_async_file:
            assert self._file_id

            bot = bot_var.get()

            async with NamedTemporaryFile("wb+") as tmp_file:
                await bot.download_file(
                    bot_id=bot_id_var.get(),
                    chat_id=chat_id_var.get(),
                    file_id=self._file_id,
                    async_buffer=tmp_file,
                )

                yield tmp_file

        else:
            assert self._content is not None

            async with NamedTemporaryFile("wb+") as tmp_file_:
                await tmp_file_.write(self._content)
                await tmp_file_.seek(0)

                yield tmp_file_


@dataclass
class AttachmentImage(BaseFileAttachment):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass
class AttachmentDocument(BaseFileAttachment):
    type: Literal[AttachmentTypes.DOCUMENT]


IncomingFile = Union[AttachmentImage, AttachmentDocument]

# TODO: Location, Contact, Link classes here
