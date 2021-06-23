from typing import BinaryIO, Dict, List, Optional, TextIO, Union
from uuid import UUID

from botx.models.base import BotXBaseModel
from botx.models.files import File
from botx.models.messages.message import Message


class SmartAppData(BotXBaseModel):
    #: meta
    headers: Dict = {}

    #: content
    body: str

    #: status
    status: int = 200


class SendingSmartApp(BotXBaseModel):
    #: uniq id of request
    ref: Optional[UUID] = None

    #:id of smartapp
    smartapp_id: UUID

    #: payload of smartapp
    data: Union[Dict, List]

    #: options of smartapp
    opts: Dict

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    #: chat of this smartapp (smartapp_id now)
    group_chat_id: UUID

    # smartapp files
    files: List[File] = []

    @classmethod
    def from_message_with_smartapp(cls, data: Union[Dict, List], message: Message):
        return cls(
            ref=message.data.ref,
            smartapp_id=message.data.smartapp_id,
            data=data,
            opts=message.data.opts,
            smartapp_api_version=message.data.smartapp_api_version,
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
    #: chat of this smartapp
    group_chat_id: UUID

    #: unread notifications count
    smartapp_counter: int

    #: options of smartapp
    opts: Dict

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    @classmethod
    def from_message_with_smartapp(cls, smartapp_counter: int, message: Message):
        return cls(
            smartapp_counter=smartapp_counter,
            opts=message.data.opts,
            smartapp_api_version=message.data.smartapp_api_version,
            group_chat_id=message.group_chat_id,
        )