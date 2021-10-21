from dataclasses import dataclass

from botx.shared_models.async_buffer import AsyncBufferReadable


@dataclass
class OutgoingAttachment:
    content: bytes
    filename: str

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
