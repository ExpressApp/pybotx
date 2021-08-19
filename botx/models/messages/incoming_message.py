"""Definition of messages received by bot or sent by it."""

from typing import Any, Dict, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseConfig, BaseModel, Field, validator

from botx.models import events
from botx.models.attachments import AttachList
from botx.models.entities import EntityList
from botx.models.enums import ChatTypes, ClientPlatformEnum, CommandTypes
from botx.models.files import File

CommandDataType = Union[
    events.ChatCreatedEvent,
    events.AddedToChatEvent,
    events.DeletedFromChatEvent,
    events.LeftFromChatEvent,
    events.InternalBotNotificationEvent,
    Dict[str, Any],
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


class DeviceMeta(BaseModel):
    """User device metadata."""

    #: could send pushes.
    pushes: Optional[bool]

    #: user timezone.
    timezone: Optional[str]

    #: app permissions (microphone, camera, etc.)
    permissions: Optional[Dict[str, Any]]


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

    #: device brand.
    manufacturer: Optional[str]

    #: device name.
    device: Optional[str]

    #: device Operating System.
    device_software: Optional[str]

    #: device metadata.
    device_meta: Optional[DeviceMeta]

    #: client platform name.
    platform: Optional[ClientPlatformEnum]

    #: platform package ID with app data and device.
    platform_package_id: Optional[str]

    #: Express app version.
    app_version: Optional[str]

    #: session locale.
    locale: Optional[str]

    #: host from which user sent message.
    host: str

    @property
    def upn(self) -> Optional[str]:
        """User principal name.

        https://docs.microsoft.com/en-us/windows/win32/adschema/a-userprincipalname
        """
        if self.ad_login and self.ad_domain:
            return "{0}@{1}".format(self.ad_login, self.ad_domain)

        return None


class IncomingMessage(BaseModel):
    """
    Message that was received by bot and should be handled.

    Warning:
         `file` is deprecated field for botx api v4+.
    """

    #: message event id on which bot should answer.
    sync_id: UUID

    #: command for bot.
    command: Command

    #: file attached to message.
    file: Optional[File] = None

    #: information about user from which message was received.
    user: Sender = Field(..., alias="from")

    #: ID of message whose ui element was triggered to send this message.
    source_sync_id: Optional[UUID] = None

    #: id of bot that should handle message.
    bot_id: UUID

    #: additional entities that can be received by bot.
    entities: EntityList = Field([])

    #: attached documents and files to message.
    attachments: AttachList = Field([])

    class Config(BaseConfig):
        allow_population_by_field_name = True

    @validator("file", always=True, pre=True)
    def skip_file_validation(
        cls,
        file: Optional[Union[dict, File]],  # noqa: N805
    ) -> Optional[File]:
        """Skip validation for incoming file since users have not such limits as bot.

        Arguments:
            file: file data that should be used for building file instance.

        Returns:
            Constructed file.
        """
        if isinstance(file, File):
            return file
        elif file is not None:
            return File.construct(**file)

        return None
