from io import BytesIO, StringIO

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
