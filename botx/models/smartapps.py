"""Definition of smartapp object."""

from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Union
from uuid import UUID

from botx.models.base import BotXBaseModel
from botx.models.files import File, MetaFile
from botx.models.messages.message import Message


class SendingSmartAppEvent(BotXBaseModel):
    """SmartApp event with data."""

    #: unique request id
    ref: Optional[UUID] = None

    #: smartapp id
    smartapp_id: UUID

    #: event data
    data: Dict[str, Any]  # noqa: WPS110

    #: event options
    opts: Dict[str, Any] = {}

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    #: smartapp chat
    group_chat_id: Optional[UUID]

    #: files
    files: List[File] = []

    #: file's meta to upload
    async_files: List[MetaFile] = []

    @classmethod
    def from_message(
        cls,
        data: Dict[str, Any],  # noqa: WPS110
        message: Message,
    ) -> "SendingSmartAppEvent":
        """Build smartapp event from message.

        Arguments:
            data: smartapp's data.
            message: incoming message.

        Returns:
            Built smartapp event.
        """
        return cls(
            ref=message.data["ref"],
            smartapp_id=message.data["smartapp_id"],
            data=data,
            opts=message.data["opts"],
            smartapp_api_version=message.data["smartapp_api_version"],
            group_chat_id=message.group_chat_id,
        )

    def add_file(
        self,
        file: Union[TextIO, BinaryIO, File],
        filename: Optional[str] = None,
    ) -> None:
        """Attach file to smartapp.

        Arguments:
            file: file that should be attached to the message.
            filename: name for file that will be used if if can not be retrieved from
                file.
        """
        if isinstance(file, File):
            file.file_name = filename or file.file_name
            self.files.append(file)
        else:
            self.files.append(File.from_file(file, filename=filename))


class SendingSmartAppNotification(BotXBaseModel):
    """SmartApp notification with counter."""

    #: smartapp chat
    group_chat_id: Optional[UUID]

    #: unread notifications count
    smartapp_counter: int

    #: event options
    opts: Dict[str, Any] = {}

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    @classmethod
    def from_message(
        cls,
        smartapp_counter: int,
        message: Message,
    ) -> "SendingSmartAppNotification":
        """Build smartapp notification from message.

        Arguments:
            smartapp_counter: smartapp notification counter.
            message: incoming message.

        Returns:
            Built smartapp notification.
        """
        return cls(
            smartapp_counter=smartapp_counter,
            opts=message.data["opts"],
            smartapp_api_version=message.data["smartapp_api_version"],
            group_chat_id=message.group_chat_id,
        )
