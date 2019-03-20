from uuid import UUID

from botx import Message, SyncID


def test_message_sync_id_is_sync_id_instance(command_with_text_and_file):
    assert isinstance(Message(**command_with_text_and_file).sync_id, SyncID)


def test_message_command(command_with_text_and_file):
    m = Message(**command_with_text_and_file)
    cmd = m.command
    assert cmd.body == command_with_text_and_file["command"]["body"]
    assert cmd.cmd == command_with_text_and_file["command"]["body"].split(" ", 1)[0]
    assert cmd.cmd_arg == "".join(
        command_with_text_and_file["command"]["body"].split(" ", 1)[1:]
    )


def test_message_properties(command_with_text_and_file):
    m = Message(**command_with_text_and_file)
    assert m.body == m.command.body == command_with_text_and_file["command"]["body"]
    assert m.data == m.command.data == command_with_text_and_file["command"]["data"]
    assert (
        m.user_huid
        == m.user.user_huid
        == UUID(command_with_text_and_file["from"]["user_huid"])
    )
    assert (
        m.ad_login == m.user.ad_login == command_with_text_and_file["from"]["ad_login"]
    )
    assert (
        m.group_chat_id
        == m.user.group_chat_id
        == UUID(command_with_text_and_file["from"]["group_chat_id"])
    )
    assert (
        m.chat_type
        == m.user.chat_type
        == command_with_text_and_file["from"]["chat_type"]
    )
    assert m.host == m.user.host == command_with_text_and_file["from"]["host"]
