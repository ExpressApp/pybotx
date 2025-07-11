import os
import pytest
from typing import Optional

from pybotx.async_buffer import (
    AsyncBufferReadable,
    AsyncBufferWritable,
    get_file_size,
)


class ConcreteAsyncBuffer(AsyncBufferReadable, AsyncBufferWritable):
    """Concrete implementation of AsyncBufferReadable and AsyncBufferWritable for testing."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._position = 0

    async def seek(self, cursor: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            self._position = cursor
        elif whence == os.SEEK_CUR:
            self._position += cursor
        elif whence == os.SEEK_END:
            self._position = len(self._buffer) + cursor
        return self._position

    async def tell(self) -> int:
        return self._position

    async def write(self, content: bytes) -> int:
        if self._position == len(self._buffer):
            # Append to the end
            self._buffer.extend(content)
        else:
            # Insert or overwrite
            self._buffer[self._position : self._position + len(content)] = content
        self._position += len(content)
        return len(content)

    async def read(self, bytes_to_read: Optional[int] = None) -> bytes:
        if bytes_to_read is None:
            result = bytes(self._buffer[self._position :])
            self._position = len(self._buffer)
        else:
            result = bytes(
                self._buffer[self._position : self._position + bytes_to_read]
            )
            self._position += min(bytes_to_read, len(self._buffer) - self._position)
        return result


@pytest.mark.asyncio
async def test_async_buffer_base_protocol() -> None:
    """Test AsyncBufferBase protocol methods."""
    buffer = ConcreteAsyncBuffer()

    # Test seek and tell
    position = await buffer.seek(10)
    assert position == 10

    position = await buffer.tell()
    assert position == 10


@pytest.mark.asyncio
async def test_async_buffer_writable_protocol() -> None:
    """Test AsyncBufferWritable protocol methods."""
    buffer = ConcreteAsyncBuffer()

    # Test write
    content = b"Hello, World!"
    bytes_written = await buffer.write(content)
    assert bytes_written == len(content)

    # Verify content was written
    await buffer.seek(0)
    read_content = await buffer.read()
    assert read_content == content


@pytest.mark.asyncio
async def test_async_buffer_readable_protocol() -> None:
    """Test AsyncBufferReadable protocol methods."""
    buffer = ConcreteAsyncBuffer()

    # Write some content
    content = b"Hello, World!"
    await buffer.write(content)

    # Test read
    await buffer.seek(0)
    read_content = await buffer.read(5)
    assert read_content == b"Hello"

    # Test read with no bytes_to_read
    read_content = await buffer.read()
    assert read_content == b", World!"


@pytest.mark.asyncio
async def test_get_file_size() -> None:
    """Test get_file_size function."""
    buffer = ConcreteAsyncBuffer()

    # Write some content
    content = b"Hello, World!"
    await buffer.write(content)

    # Test get_file_size
    file_size = await get_file_size(buffer)
    assert file_size == len(content)

    # Verify position is reset to 0
    position = await buffer.tell()
    assert position == 0
