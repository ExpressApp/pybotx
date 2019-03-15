import base64
import uuid

import pytest
from pydantic import ValidationError

from botx import *


def test_bubble_element():
    b = BubbleElement(command="cmd")
    assert b.command == "cmd"
    assert b.label == b.command

    b = BubbleElement(command="cmd", label="label")
    assert b.command == "cmd"
    assert b.label == "label"


def test_message_command():
    m = MessageCommand(body="/doit")
    assert m.body == "/doit"
    assert m.cmd == "/doit"
    assert m.cmd_arg == ""
    assert m.data == {}

    m = MessageCommand(body="/doit arg")
    assert m.body == "/doit arg"
    assert m.cmd == "/doit"
    assert m.cmd_arg == "arg"
    assert m.data == {}

    m = MessageCommand(body="/doit arg1 arg2", data={"field": 42})
    assert m.body == "/doit arg1 arg2"
    assert m.cmd == "/doit"
    assert m.cmd_arg == "arg1 arg2"
    assert m.data == {"field": 42}


def test_keyboard_element():
    k = KeyboardElement(command="cmd")
    assert k.command == "cmd"
    assert k.label == "cmd"

    k = KeyboardElement(command="cmd", label="label")
    assert k.command == "cmd"
    assert k.label == "label"


def test_message():
    with pytest.raises(ValidationError):
        MessageUser(
            group_chat_id=uuid.uuid4(), chat_type="wrong_type", host="cts.test.ru"
        )
    user = MessageUser(
        group_chat_id=uuid.uuid4(), chat_type=ChatTypeEnum.chat, host="cts.test.ru"
    )
    m = Message(
        sync_id=uuid.uuid4(),
        command=MessageCommand(body="/doit"),
        user=user,
        bot_id=uuid.uuid4(),
    )

    assert "from" in m.dict()
    assert "from" in Message(**m.dict()).dict()
    assert m.dict()["from"] == m.user
