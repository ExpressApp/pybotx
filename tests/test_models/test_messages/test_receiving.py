import uuid
from datetime import datetime as dt, timezone as tz
from typing import List

import pytest

from botx import ChatTypes, CommandTypes, EntityTypes
from botx.models.messages.incoming_message import Command, IncomingMessage, Sender


@pytest.mark.parametrize(
    ("body", "command", "arguments", "single_argument"),
    [
        ("/command", "/command", (), ""),
        ("/command ", "/command", (), ""),
        ("/command arg", "/command", ("arg",), "arg"),
        ("/command arg ", "/command", ("arg",), "arg"),
        ("/command  \t\t arg ", "/command", ("arg",), "arg"),
        ("/command arg arg", "/command", ("arg", "arg"), "arg arg"),
        ("/command     arg arg    ", "/command", ("arg", "arg"), "arg arg"),
    ],
)
def test_command_splits_right(
    body: str, command: str, arguments: List[str], single_argument: str,
) -> None:
    command = Command(body=body, command_type=CommandTypes.user)
    assert command.body == body
    assert command.command == command.command
    assert command.arguments == arguments
    assert command.single_argument == command.single_argument


def test_command_data_as_dict() -> None:
    command = Command(
        body="/test", command_type=CommandTypes.user, data={"some": "data"},
    )
    assert command.data_dict == command.data == {"some": "data"}


def test_user_email_when_credentials_passed() -> None:
    sender = Sender(
        user_huid=uuid.uuid4(),
        group_chat_id=uuid.uuid4(),
        chat_type=ChatTypes.chat,
        ad_login="user",
        ad_domain="example.com",
        username="test user",
        is_admin=False,
        is_creator=True,
        host="cts.example.com",
    )
    assert sender.upn == "user@example.com"


def test_user_email_when_credentials_missed() -> None:
    assert (
        Sender(
            group_chat_id=uuid.uuid4(),
            chat_type=ChatTypes.chat,
            is_admin=False,
            is_creator=True,
            host="cts.example.com",
        ).upn
        is None
    )


def test_skip_validation_for_file() -> None:
    file_data = {"file_name": "zen.py", "data": "data:text/plain;base64,"}

    IncomingMessage.parse_obj(
        {
            "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
            "command": {"body": "/cmd", "command_type": "user", "data": {}},
            "file": file_data,
            "from": {
                "user_huid": None,
                "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "ad_login": None,
                "ad_domain": None,
                "username": None,
                "chat_type": "group_chat",
                "host": "cts.ccteam.ru",
                "is_admin": False,
                "is_creator": False,
            },
            "bot_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
        },
    )


def test_parse_message_forward() -> None:
    inserted_at = dt(2020, 7, 10, 10, 12, 58, 420000, tzinfo=tz.utc)

    IncomingMessage.parse_obj(
        {
            "bot_id": "f6615a30-9d3d-5770-b453-749ea562a974",
            "command": {
                "body": "Message body",
                "command_type": CommandTypes.user,
                "data": {},
                "metadata": {},
            },
            "entities": [
                {
                    "data": {
                        "forward_type": ChatTypes.chat,
                        "group_chat_id": "b51df4c1-3834-0949-1066-614ec424d28a",
                        "sender_huid": "4471289e-5b52-5c1b-8eab-a22c548fef9b",
                        "source_chat_name": "MessageAuthor Name",
                        "source_inserted_at": inserted_at,
                        "source_sync_id": "80d2c3a9-0031-50a8-aeed-32bb5d285758",
                    },
                    "type": EntityTypes.forward,
                },
            ],
            "file": None,
            "sync_id": "eeb8eeca-3f31-5037-8b41-84de63909a31",
            "user": {
                "ad_domain": "ccsteam.ru",
                "ad_login": "message.forwarder",
                "chat_type": ChatTypes.chat,
                "group_chat_id": "070d866f-fe5b-0222-2a9e-b7fc35c99465",
                "host": "cts.ccsteam.ru",
                "is_admin": True,
                "is_creator": True,
                "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
                "username": "MessageForwarder Name",
            },
        },
    )
