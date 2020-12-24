from io import BytesIO, StringIO

import aiofiles
import pytest

from botx import File


@pytest.mark.parametrize("extension", [".docx", ".txt", ".html", ".pdf"])
def test_file_creation_with_right_extension(extension):
    File(file_name=f"tmp{extension}", data="")


@pytest.mark.parametrize(
    ("io_cls", "file_data", "file_name"),
    [(StringIO, "test", "test.txt"), (BytesIO, b"test", "test.txt")],
)
@pytest.mark.parametrize("explicit_file_name", ["test2.txt", None])
def test_creating_file_from_io_with_name(
    io_cls, file_data, file_name, explicit_file_name,
):
    created_file = io_cls(file_data)
    if not explicit_file_name:
        created_file.name = file_name

    assert File.from_file(created_file, filename=explicit_file_name) == File(
        file_name=explicit_file_name or file_name,
        data="data:text/plain;base64,dGVzdA==",
    )


@pytest.mark.parametrize("file_data", ["test", b"test"])
def test_creating_file_from_string(file_data):
    assert File.from_string(file_data, filename="test.txt") == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA==",
    )


@pytest.fixture()
def filename():
    return "test.txt"


@pytest.fixture()
def origin_data():
    return b"Hello,\nworld!"


@pytest.fixture()
def encoded_data():
    return "data:text/plain;base64,SGVsbG8sCndvcmxkIQ=="


@pytest.fixture()
def temp_file(tmp_path, filename, origin_data):
    file_path = tmp_path / filename
    file_path.write_bytes(origin_data)

    return file_path


@pytest.mark.asyncio
async def test_async_from_file(temp_file, encoded_data):
    async with aiofiles.open(temp_file, "rb") as fo:
        file = await File.async_from_file(fo)

    assert file.file_name == temp_file.name
    assert file.data == encoded_data


def test_file_chunks(filename, encoded_data, origin_data):
    file = File.construct(file_name=filename, data=encoded_data)
    temp_file = BytesIO()

    with file.file_chunks() as chunks:
        for chunk in chunks:
            temp_file.write(chunk)

    temp_file.seek(0)

    assert temp_file.read() == origin_data
