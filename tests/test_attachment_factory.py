from __future__ import annotations

from pathlib import Path

import aiofiles
import pytest

from pybotx.domain.attachment_factory import AttachmentFactory as AttachmentFactoryProxy
from pybotx.domain.models.attachments import OutgoingAttachment
from pybotx.domain.ports import AttachmentFactoryPort
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory


class _DummyFactory:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def from_path(self, path, *, filename=None):  # type: ignore[override]
        self.calls.append("from_path")
        return OutgoingAttachment(content=b"path", filename=filename or "path.bin")

    async def from_bytes(self, content, *, filename):  # type: ignore[override]
        self.calls.append("from_bytes")
        return OutgoingAttachment(content=content, filename=filename)

    async def from_file(self, file, *, filename=None):  # type: ignore[override]
        self.calls.append("from_file")
        return OutgoingAttachment(content=b"file", filename=filename or "file.bin")


@pytest.mark.asyncio
async def test__attachment_factory_proxy__delegates() -> None:
    dummy = _DummyFactory()
    proxy = AttachmentFactoryProxy(dummy)

    result = await proxy.from_bytes(b"data", filename="data.bin")

    assert result.content == b"data"
    assert result.filename == "data.bin"
    assert dummy.calls == ["from_bytes"]


def test__attachment_factory_port_importable() -> None:
    assert AttachmentFactoryPort is not None


@pytest.mark.asyncio
async def test__attachment_factory_proxy__delegates_path_and_file(
    tmp_path: Path,
) -> None:
    dummy = _DummyFactory()
    proxy = AttachmentFactoryProxy(dummy)
    file_path = tmp_path / "file.bin"
    file_path.write_bytes(b"payload")

    await proxy.from_path(file_path)
    await proxy.from_file(_NoNameFile(b"payload"), filename="name.bin")

    assert dummy.calls == ["from_path", "from_file"]


@pytest.mark.asyncio
async def test__attachment_factory__from_bytes() -> None:
    factory = AttachmentFactory()

    result = await factory.from_bytes(b"hello", filename="greet.txt")

    assert result.content == b"hello"
    assert result.filename == "greet.txt"


@pytest.mark.asyncio
async def test__attachment_factory__from_path(tmp_path: Path) -> None:
    factory = AttachmentFactory()
    file_path = tmp_path / "sample.txt"
    file_path.write_bytes(b"payload")

    result = await factory.from_path(file_path)

    assert result.content == b"payload"
    assert result.filename == "sample.txt"


@pytest.mark.asyncio
async def test__attachment_factory__from_file_sync(tmp_path: Path) -> None:
    factory = AttachmentFactory()
    file_path = tmp_path / "sync.bin"
    file_path.write_bytes(b"sync-data")

    with file_path.open("rb") as handle:
        result = await factory.from_file(handle)

    assert result.content == b"sync-data"
    assert result.filename == "sync.bin"


@pytest.mark.asyncio
async def test__attachment_factory__from_file_async(tmp_path: Path) -> None:
    factory = AttachmentFactory()
    file_path = tmp_path / "async.bin"
    file_path.write_bytes(b"async-data")

    async with aiofiles.open(file_path, "rb") as handle:
        result = await factory.from_file(handle, filename="override.bin")

    assert result.content == b"async-data"
    assert result.filename == "override.bin"


@pytest.mark.asyncio
async def test__attachment_factory__from_file_requires_name() -> None:
    factory = AttachmentFactory()

    with pytest.raises(ValueError, match="filename"):
        await factory.from_file(_NoNameFile(b"data"))


class _NoNameFile:
    def __init__(self, content: bytes) -> None:
        self._content = content

    def read(self) -> bytes:
        return self._content


@pytest.mark.asyncio
async def test__attachment_factory__from_file_without_read_raises() -> None:
    factory = AttachmentFactory()

    with pytest.raises(TypeError, match="read method"):
        await factory.from_file(_NoReadFile(), filename="name.bin")


class _NoReadFile:
    pass
