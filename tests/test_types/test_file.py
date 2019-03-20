import base64

from botx import File, Message


def test_file_properties(command_with_text_and_file):
    m = Message(**command_with_text_and_file)
    assert m.file.file_name == command_with_text_and_file["file"]["file_name"]
    assert m.file.raw_data == base64.b64decode(
        command_with_text_and_file["file"]["data"].split(",", 1)[1]
    )
    assert m.file.media_type == "application/json"


def test_data_from_file(command_with_text_and_file):
    m = Message(**command_with_text_and_file)
    with open(
        f"tests/files/{command_with_text_and_file['file']['file_name']}", "rb"
    ) as original_file:
        for message_file_line, line in zip(m.file.file, original_file):
            assert message_file_line == line


def test_binary_file_serializing(binary_gif_file, binary_img_file):
    with open(f"tests/files/{binary_img_file['file_name']}", "rb") as f:
        mfile = File.from_file(f)
        assert File(**binary_img_file) == mfile
        assert (
            mfile.media_type
            == binary_img_file["data"].split("data:", 1)[1].split(";", 1)[0]
        )

    with open(f"tests/files/{binary_gif_file['file_name']}", "rb") as f:
        mfile = File.from_file(f)
        assert File(**binary_gif_file) == mfile
        assert (
            mfile.media_type
            == binary_gif_file["data"].split("data:", 1)[1].split(";", 1)[0]
        )


def test_text_file_serializing(text_txt_file, text_json_file):
    with open(f"tests/files/{text_txt_file['file_name']}", "r") as f:
        mfile = File.from_file(f)
        assert File(**text_txt_file) == mfile
        assert (
            mfile.media_type
            == text_txt_file["data"].split("data:", 1)[1].split(";", 1)[0]
        )

    with open(f"tests/files/{text_json_file['file_name']}", "r") as f:
        mfile = File.from_file(f)
        assert File(**text_json_file) == mfile
        assert (
            mfile.media_type
            == text_json_file["data"].split("data:", 1)[1].split(";", 1)[0]
        )
