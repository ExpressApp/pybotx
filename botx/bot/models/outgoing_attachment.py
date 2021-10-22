from dataclasses import dataclass

from botx.shared_models.async_buffer import AsyncBufferReadable

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
