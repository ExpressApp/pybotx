import uuid
from typing import List

import pytest

from botx import ChatTypes, CommandTypes
from botx.models.receiving import Command, User


@pytest.mark.parametrize(
    "body, command, arguments, single_argument",
    (
        ("/command", "/command", tuple(), ""),
        ("/command ", "/command", tuple(), ""),
        ("/command arg", "/command", ("arg",), "arg"),
        ("/command arg ", "/command", ("arg",), "arg"),
        ("/command  \t\t arg ", "/command", ("arg",), "arg"),
        ("/command arg arg", "/command", ("arg", "arg"), "arg arg"),
        ("/command     arg arg    ", "/command", ("arg", "arg"), "arg arg"),
    ),
)
def test_command_splits_right(
    body: str, command: str, arguments: List[str], single_argument: str
) -> None:
    command = Command(body=body, command_type=CommandTypes.user)
    assert command.body == body
    assert command.command == command.command
    assert command.arguments == arguments
    assert command.single_argument == command.single_argument


def test_command_data_as_dict() -> None:
    command = Command(
        body="/test", command_type=CommandTypes.user, data={"some": "data"}
    )
    assert command.data_dict == command.data == {"some": "data"}


def test_user_email_when_credentials_passed() -> None:
    assert (
        User(
            user_huid=uuid.uuid4(),
            group_chat_id=uuid.uuid4(),
            chat_type=ChatTypes.chat,
            ad_login="user",
            ad_domain="example.com",
            username="test user",
            is_admin=False,
            is_creator=True,
            host="cts.example.com",
        ).email
        == "user@example.com"
    )


def test_user_email_when_credentials_missed() -> None:
    assert (
        User(
            group_chat_id=uuid.uuid4(),
            chat_type=ChatTypes.chat,
            is_admin=False,
            is_creator=True,
            host="cts.example.com",
        ).email
        is None
    )
