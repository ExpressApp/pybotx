from typing import Optional

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS440


class AsyncBufferBase(Protocol):
    async def seek(self, cursor: int) -> int:
        ...  # noqa: WPS428


class AsyncBufferWritable(AsyncBufferBase):
    async def write(self, content: bytes) -> int:
        ...  # noqa: WPS428


class AsyncBufferReadable(AsyncBufferBase):
    async def read(self, bytes_to_read: Optional[int] = None) -> bytes:
        ...  # noqa: WPS428
