"""Builder for messages in tests."""

import uuid
from dataclasses import field
from typing import Any, List, Optional

from pydantic import BaseConfig, validator
from pydantic.dataclasses import dataclass

from botx import ChatMention, Mention, MentionTypes, UserMention
from botx.models import enums
from botx.models.enums import ChatTypes, EntityTypes
from botx.models.messages.incoming_message import (
    Command,
    Entity,
    IncomingMessage,
    Sender,
)
from botx.testing.building.validators import (
    convert_to_acceptable_file,
    validate_body_corresponds_command,
    validate_command_type_corresponds_command,
)


def _build_default_user() -> Sender:
    return Sender(
        user_huid=uuid.uuid4(),
        group_chat_id=uuid.uuid4(),
        chat_type=ChatTypes.chat,
        ad_login="test_user",
        ad_domain="example.com",
        username="Test User",
        is_admin=True,
        is_creator=True,
        host="cts.example.com",
    )


class BuilderConfig(BaseConfig):
    """Config for builder dataclass."""

    validate_assignment = True


@dataclass(config=BuilderConfig)
class MessageBuilder:
    """Builder for command message for bot."""

    bot_id: uuid.UUID = field(default_factory=uuid.uuid4)

    command_data: dict = field(default_factory=dict)
    system_command: bool = field(default=False)
    file: Optional[Any] = field(default=None)
    user: Sender = field(default_factory=_build_default_user)
    entities: List[Entity] = field(default_factory=list)
    body: str = field(default="")

    _body_and_command_validator = validator("body", always=True)(
        validate_body_corresponds_command,
    )
    _command_type_and_data_validator = validator("system_command", always=True)(
        validate_command_type_corresponds_command,
    )
    _file_converter = validator("file", always=True)(convert_to_acceptable_file)

    @property
    def message(self) -> IncomingMessage:
        """Message that was built by builder."""
        command_type = (
            enums.CommandTypes.system
            if self.system_command
            else enums.CommandTypes.user
        )
        command = Command(
            body=self.body, command_type=command_type, data=self.command_data,
        )
        return IncomingMessage(
            sync_id=uuid.uuid4(),
            command=command,
            file=self.file,
            bot_id=self.bot_id,
            user=self.user,
            entities=self.entities,
        )

    def mention_contact(self, user_huid: uuid.UUID) -> None:
        """Add contact mention to message for bot.

        Arguments:
            user_huid: huid of user to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=UserMention(user_huid=user_huid),
                    mention_type=MentionTypes.contact,
                ),
            ),
        )

    def mention_user(self, user_huid: uuid.UUID) -> None:
        """Add user mention to message for bot.

        Arguments:
            user_huid: huid of user to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(mention_data=UserMention(user_huid=user_huid)),
            ),
        )

    def mention_chat(self, chat_id: uuid.UUID) -> None:
        """Add chat mention to message for bot.

        Arguments:
            chat_id: id of chat to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=ChatMention(group_chat_id=chat_id),
                    mention_type=MentionTypes.chat,
                ),
            ),
        )
