"""Definition of messages received by bot or sent by it."""

from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseConfig, BaseModel, Field, validator

from botx.models import events
from botx.models.enums import ChatTypes, CommandTypes, EntityTypes
from botx.models.files import File
from botx.models.forwards import Forward
from botx.models.mentions import Mention

CommandDataType = Union[
    events.ChatCreatedEvent, events.AddedToChatEvent, Dict[str, Any],
]


class Command(BaseModel):
    """Command that should be proceed by bot."""

    #: incoming text message.
    body: str

    #: was command received from user or this is system event.
    command_type: CommandTypes

    #: command payload.
    data: CommandDataType = {}  # noqa: WPS110

    #: command metadata.
    metadata: Dict[str, Any] = {}

    @property
    def command(self) -> str:
        """First word of body that was sent to bot."""
        return self.body.split(" ", 1)[0]

    @property
    def arguments(self) -> Tuple[str, ...]:
        """Words that are passed after command."""
        words = (word for word in self.body.split(" ")[1:])
        arguments = (arg for arg in words if arg and not arg.isspace())

        return tuple(arguments)

    @property
    def single_argument(self) -> str:
        """Line that passed after command."""
        body_len = len(self.command)
        return self.body[body_len:].strip()

    @property
    def data_dict(self) -> dict:
        """Command data as dictionary."""
        if isinstance(self.data, dict):
            return self.data
        return self.data.dict()


class Sender(BaseModel):
    """User that sent message to bot."""

    #: user id.
    user_huid: Optional[UUID]

    #: chat id.
    group_chat_id: UUID

    #: type of chat.
    chat_type: ChatTypes

    #: AD login of user.
    ad_login: Optional[str]

    #: AD domain of user.
    ad_domain: Optional[str]

    #: username of user.
    username: Optional[str]

    #: is user admin of chat.
    is_admin: Optional[bool]

    #: is user creator of chat.
    is_creator: Optional[bool]

    #: host from which user sent message.
    host: str

    @property
    def email(self) -> Optional[str]:
        """User email."""
        if self.ad_login and self.ad_domain:
            return "{0}@{1}".format(self.ad_login, self.ad_domain)

        return None


class Entity(BaseModel):
    """Additional entity that can be received by bot."""

    #: entity type.
    type: EntityTypes  # noqa: WPS: 125

    #: entity data.
    data: Union[Forward, Mention]  # noqa: WPS110


class IncomingMessage(BaseModel):
    """Message that was received by bot and should be handled."""

    #: message event id on which bot should answer.
    sync_id: UUID

    #: command for bot.
    command: Command

    #: file attached to message.
    file: Optional[File] = None

    #: information about user from which message was received.
    user: Sender = Field(..., alias="from")

    #: id of bot that should handle message.
    bot_id: UUID

    #: additional entities that can be received by bot.
    entities: List[Entity] = []

    class Config(BaseConfig):
        allow_population_by_field_name = True

    @validator("file", always=True, pre=True)
    def skip_file_validation(
        cls, file: Optional[Union[dict, File]],  # noqa: N805
    ) -> Optional[File]:
        """Skip validation for incoming file since users have not such limits as bot.

        Arguments:
            cls: this class.
            file: file data that should be used for building file instance.

        Returns:
            Constructed file.
        """
        if isinstance(file, File):
            return file
        elif file is not None:
            return File.construct(**file)

        return None
