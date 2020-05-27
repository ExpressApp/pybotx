"""Builder for messages in tests."""

import uuid
from typing import BinaryIO, List, Optional, TextIO, Union

from botx import ChatMention, Mention, MentionTypes, UserMention
from botx.models import enums, events, files, receiving
from botx.models.enums import ChatTypes, EntityTypes
from botx.models.receiving import Entity


# There are a lot of properties and functions here, since message is a complex type
# that should be carefully validated.
# Properties are count as normal functions, so disable
# 1) too many methods (a lot of properties)
# 2) block variables overlap (setters are counted as replacement for functions)
class MessageBuilder:
    """Builder for command message for bot."""

    def __init__(
        self,
        body: str = "",
        bot_id: Optional[uuid.UUID] = None,
        user: Optional[receiving.User] = None,
    ) -> None:
        """Init builder with required params.

        Arguments:
            body: command body.
            bot_id: id of bot that will be autogenerated if not passed.
            user: user from which command was received.
        """
        self._user: receiving.User = user or self._default_user
        self._bot_id = bot_id or uuid.uuid4()
        self._body: str = ""
        self._is_system_command: bool = False
        self._command_data: dict = {}
        self._file: Optional[files.File] = None
        self._entities: List[Entity] = []

        # checks for special invariants for events
        self._event_checkers = {
            events.SystemEvents.chat_created: self._check_chat_created_event,
            events.SystemEvents.file_transfer: self._check_file_transfer_event,
        }

        self.body = body

    @property
    def bot_id(self) -> uuid.UUID:
        """Id of bot."""
        return self._bot_id

    @bot_id.setter
    def bot_id(self, bot_id: uuid.UUID) -> None:
        """Id of bot."""
        self._bot_id = bot_id

    @property
    def body(self) -> str:
        """Message body."""
        return self._body

    @body.setter
    def body(self, body: str) -> None:
        """Message body."""
        self._check_system_command_properties(
            body, self._is_system_command, self._command_data,
        )
        self._body = body

    @property
    def command_data(self) -> dict:
        """Additional command data."""
        return self._command_data

    @command_data.setter
    def command_data(self, command_data: dict) -> None:
        """Additional command data."""
        self._command_data = command_data

    @property
    def system_command(self) -> bool:
        """Is command a system event."""
        return self._is_system_command

    @system_command.setter
    def system_command(self, is_system_command: bool) -> None:
        """Is command a system event."""
        self._check_system_command_properties(
            self._body, is_system_command, self._command_data,
        )
        self._is_system_command = is_system_command

    @property
    def file(self) -> Optional[files.File]:
        """File attached to message."""
        return self._file

    @file.setter
    def file(self, file: Optional[Union[files.File, BinaryIO, TextIO]]) -> None:
        """File that will be attached to message."""
        if isinstance(file, files.File) or file is None:
            self._file = file
        else:
            self._file = files.File.from_file(file, filename="temp.txt")
            self._file.file_name = file.name

    @property
    def user(self) -> receiving.User:
        """User from which message will be received."""
        return self._user

    @user.setter
    def user(self, user: receiving.User) -> None:
        """User from which message will be received."""
        self._user = user

    @property
    def entities(self) -> List[Entity]:
        """Additional entities in message."""
        return self._entities

    @entities.setter
    def entities(self, entities: List[Entity]) -> None:
        """Additional entities in message."""
        self._entities = entities

    @property
    def message(self) -> receiving.IncomingMessage:
        """Message that was built by builder."""
        command_type = (
            enums.CommandTypes.system
            if self.system_command
            else enums.CommandTypes.user
        )
        command = receiving.Command(
            body=self.body, command_type=command_type, data=self.command_data,
        )
        return receiving.IncomingMessage(
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
        self._entities.append(
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
        self._entities.append(
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
        self._entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=ChatMention(group_chat_id=chat_id),
                    mention_type=MentionTypes.chat,
                ),
            ),
        )

    @property
    def _default_user(self) -> receiving.User:
        """User that will be used in __init__ as fallback."""
        return receiving.User(
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

    def _check_system_command_properties(
        self, body: str, is_system_command: bool, command_data: dict,
    ) -> None:
        """Check that system event message is valid.

        Arguments:
            body: message body.
            is_system_command: flag that command is system event.
            command_data: additional data that will be included into message and should
                be validated.
        """
        if is_system_command:
            event = events.SystemEvents(body)  # check that is real system event
            event_shape = events.EVENTS_SHAPE_MAP.get(event)
            if event_shape:
                event_shape.parse_obj(command_data)  # check event data
            self._event_checkers[event]()

    def _check_chat_created_event(self) -> None:
        """Check invariants for `system:chat_created` event."""
        assert (
            not self.user.user_huid
        ), "A user in system:chat_created can not have user_huid"
        assert (
            not self.user.ad_login
        ), "A user in system:chat_created can not have ad_login"
        assert (
            not self.user.ad_domain
        ), "A user in system:chat_created can not have ad_domain"
        assert (
            not self.user.username
        ), "A user in system:chat_created can not have username"

    def _check_file_transfer_event(self) -> None:
        """Check invariants for `file_transfer` event."""
        assert self.file, "file_transfer event should have attached file"
