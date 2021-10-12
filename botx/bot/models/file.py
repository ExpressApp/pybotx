from dataclasses import dataclass
from typing import Optional

from botx.client.files_api.download_file import (
    AsyncBufferReadable,
    get_async_buffer_filename,
)


@dataclass
class OutgoingFile:
    _content: bytes
    filename: str
    _is_async_file: bool = False

    @classmethod
    async def from_async_buffer(
        cls,
        async_buffer: AsyncBufferReadable,
        filename: Optional[str] = None,
    ) -> "OutgoingFile":
        return cls(
            _content=await async_buffer.read(),
            filename=filename or get_async_buffer_filename(async_buffer),
        )
