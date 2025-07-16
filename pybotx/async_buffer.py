import abc
import os
from typing import Optional

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


class AsyncBufferBase(Protocol):
    async def seek(
        self,
        cursor: int,
        whence: int = os.SEEK_SET,
    ) -> int: ...  # pragma: no cover

    async def tell(self) -> int: ...  # pragma: no cover


class AsyncBufferWritable(AsyncBufferBase):
    @abc.abstractmethod
    async def write(self, content: bytes) -> int: ...  # pragma: no cover


class AsyncBufferReadable(AsyncBufferBase):
    @abc.abstractmethod
    async def read(
        self,
        bytes_to_read: Optional[int] = None,
    ) -> bytes: ...  # pragma: no cover


async def get_file_size(async_buffer: AsyncBufferReadable) -> int:
    await async_buffer.seek(0, os.SEEK_END)
    file_size = await async_buffer.tell()
    await async_buffer.seek(0)
    return file_size
