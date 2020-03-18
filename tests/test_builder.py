from io import StringIO

from botx import File, IncomingMessage
from botx.testing import MessageBuilder


def test_setting_new_file_from_file() -> None:
    file = File.from_string("some data", "name.txt")
    builder = MessageBuilder()
    builder.file = file

    assert builder.file == file


def test_setting_new_file_from_io() -> None:
    file = File.from_string("some data", "name.txt")
    builder = MessageBuilder()
    builder.file = file.file

    assert builder.file == file


def test_settings_new_user_for_message(incoming_message: IncomingMessage) -> None:
    builder = MessageBuilder()
    builder.user = incoming_message.user

    assert builder.user == incoming_message.user


def test_file_transfer_event() -> None:
    builder = MessageBuilder()
    builder.file = File.from_string("some data", "name.txt")

    builder.body = "file_transfer"
    builder.system_command = True


def test_setting_not_processable_file_for_incoming_message() -> None:
    file = StringIO("import this")
    file.name = "zen.py"

    builder = MessageBuilder()
    builder.file = file

    message = builder.message

    assert message.file.file_name == "zen.py"
