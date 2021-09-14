from botx import File


def test_retrieving_file_data_in_bytes():
    assert File.from_string(b"test", filename="test.txt").data_in_bytes == b"test"


def test_retrieving_file_data_in_base64():
    assert File.from_string(b"test", filename="test.txt").data_in_base64 == "dGVzdA=="


def test_retrieving_txt_media_type():
    assert File.from_string(b"test", filename="test.txt").media_type == "text/plain"


def test_retrieving_png_media_type():
    assert File.from_string(b"test", filename="test.png").media_type == "image/png"


def test_retrieving_file_size():
    assert File.from_string(b"file\ncontents", filename="test.txt").size_in_bytes == 13


def test_get_ext_by_unsupported_mimetype():
    assert File.get_ext_by_mimetype("application/javascript") is None
