"""Definition of messages received by bot or sent by it."""

from typing import Any, Dict, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseConfig, BaseModel, Field, validator

from botx.models.enums import ChatTypes, CommandTypes
from botx.models.events import ChatCreatedEvent
from botx.models.files import File

CommandDataType = Union[ChatCreatedEvent, Dict[str, Any]]


class Command(BaseModel):
    """Command that should be proceed by bot."""

    body: str
    """incoming text message."""
    command_type: CommandTypes
    """was command received from user or this is system event."""
    data: CommandDataType = {}
    """command payload."""

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
        return self.body[len(self.command) :].strip()

    @property
    def data_dict(self) -> dict:
        """Command data as dictionary."""
        if isinstance(self.data, dict):
            return self.data
        return self.data.dict()


class User(BaseModel):
    """User that sent message to bot."""

    user_huid: Optional[UUID]
    """user id."""
    group_chat_id: UUID
    """chat id."""
    chat_type: ChatTypes
    """type of chat."""
    ad_login: Optional[str]
    """AD login of user."""
    ad_domain: Optional[str]
    """AD domain of user."""
    username: Optional[str]
    """username of user."""
    is_admin: bool
    """is user admin of chat."""
    is_creator: bool
    """is user creator of chat."""
    host: str
    """host from which user sent message."""

    @property
    def email(self) -> Optional[str]:
        """User email."""
        if self.ad_login and self.ad_domain:
            return f"{self.ad_login}@{self.ad_domain}"

        return None


class IncomingMessage(BaseModel):
    """Message that was received by bot and should be handled."""

    sync_id: UUID
    """message event id on which bot should answer."""
    command: Command
    """command for bot."""
    file: Optional[File] = None
    """file attached to message."""
    user: User = Field(..., alias="from")
    """information about user from which message was received."""
    bot_id: UUID
    """id of bot that should handle message."""

    class Config(BaseConfig):  # noqa: WPS431, D106
        allow_population_by_field_name = True

    @validator("file", always=True, pre=True)
    def skip_file_validation(
        cls, value: Optional[Union[dict, File]]  # noqa: N805
    ) -> Optional[File]:
        """Skip validation for incoming file since users have not such limits as bot.

        Arguments:
            value: file data that should be used for building file instance.

        Returns:
            Constructed file.
        """
        if isinstance(value, File):
            return value
        elif value is not None:
            return File.construct(**value)

        return None
