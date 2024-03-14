import os
from typing import Optional

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS440


class AsyncBufferBase(Protocol):
    async def seek(self, cursor: int, whence: int = os.SEEK_SET) -> int:
        ...  # noqa: WPS428

    async def tell(self) -> int:
        ...  # noqa: WPS428


class AsyncBufferWritable(AsyncBufferBase):
    async def write(self, content: bytes) -> int:
        ...  # noqa: WPS428


class AsyncBufferReadable(AsyncBufferBase):
    async def read(self, bytes_to_read: Optional[int] = None) -> bytes:
        ...  # noqa: WPS428


async def get_file_size(async_buffer: AsyncBufferReadable) -> int:
    await async_buffer.seek(0, os.SEEK_END)
    file_size = await async_buffer.tell()
    await async_buffer.seek(0)

    return file_size
