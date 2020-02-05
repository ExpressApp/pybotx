from io import BytesIO, StringIO

import pytest
from pydantic import ValidationError

from botx import File


def test_file_wont_be_created_if_extension_is_unsupported() -> None:
    for extension in {".py", ".c", ".java"}:
        with pytest.raises(ValidationError):
            _ = File(file_name=f"tmp{extension}", data="")


def test_file_will_be_created_with_right_extension() -> None:
    for extension in {".docx", ".txt", ".html", ".pdf"}:
        _ = File(file_name=f"tmp{extension}", data="")


def test_creating_from_binary_file_without_name() -> None:
    f = BytesIO(b"test")
    assert File.from_file(f, filename="test.txt") == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_binary_file_with_name() -> None:
    f = BytesIO(b"test")
    f.name = "test.txt"
    assert File.from_file(f) == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_binary_file_with_name_and_explicit_name() -> None:
    f = BytesIO(b"test")
    f.name = "test.txt"
    assert File.from_file(f, filename="test2.txt") == File(
        file_name="test2.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_text_file_without_name() -> None:
    f = StringIO("test")
    assert File.from_file(f, filename="test.txt") == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_text_file_with_name() -> None:
    f = StringIO("test")
    f.name = "test.txt"
    assert File.from_file(f) == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_text_file_with_name_and_explicit_name() -> None:
    f = StringIO("test")
    f.name = "test.txt"
    assert File.from_file(f, filename="test2.txt") == File(
        file_name="test2.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_binary_string() -> None:
    assert File.from_string(b"test", filename="test.txt") == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_creating_from_text_string() -> None:
    assert File.from_string("test", filename="test.txt") == File(
        file_name="test.txt", data="data:text/plain;base64,dGVzdA=="
    )


def test_generating_file() -> None:
    f = File.from_string(b"test", filename="test.txt").file
    assert f.name == "test.txt"
    assert f.read() == b"test"


def test_retrieving_file_data_in_bytes() -> None:
    assert File.from_string(b"test", filename="test.txt").data_in_bytes == b"test"


def test_retrieving_file_data_in_base64() -> None:
    assert File.from_string(b"test", filename="test.txt").data_in_base64 == "dGVzdA=="


def test_retrieving_file_media_type() -> None:
    assert File.from_string(b"test", filename="test.txt").media_type == "text/plain"
