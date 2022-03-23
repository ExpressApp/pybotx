from pybotx.async_buffer import AsyncBufferReadable, get_file_size
from pybotx.constants import STICKER_IMAGE_MAX_SIZE

PNG_MAGIC_BYTES: bytes = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"


async def ensure_file_content_is_png(async_buffer: AsyncBufferReadable) -> None:
    magic_bytes = await async_buffer.read(8)

    await async_buffer.seek(0)

    if magic_bytes != PNG_MAGIC_BYTES:
        raise ValueError("Passed file is not PNG")


async def ensure_sticker_image_size_valid(async_buffer: AsyncBufferReadable) -> None:
    file_size = await get_file_size(async_buffer)

    if file_size > STICKER_IMAGE_MAX_SIZE:
        max_file_size_mb = STICKER_IMAGE_MAX_SIZE / 1024 / 1024
        raise ValueError(
            f"Passed file size is greater than {max_file_size_mb:.1f} Mb",
        )
