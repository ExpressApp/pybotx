from botx import File


def test_retrieving_file_data_in_bytes():
    assert File.from_string(b"test", filename="test.txt").data_in_bytes == b"test"


def test_retrieving_file_data_in_base64():
    assert File.from_string(b"test", filename="test.txt").data_in_base64 == "dGVzdA=="


def test_retrieving_file_media_type():
    assert File.from_string(b"test", filename="test.txt").media_type == "text/plain"


def test_accept_has_supported_extension():
    correct_filename = "test.txt"
    result = File.has_supported_extension(correct_filename)

    assert result is True


def test_decline_has_supported_extension():
    bad_filename = "test.bad"
    result = File.has_supported_extension(bad_filename)

    assert result is False
