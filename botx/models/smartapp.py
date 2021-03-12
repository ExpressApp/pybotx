from typing import Dict, Union, List
from uuid import UUID

from botx.models.base import BotXBaseModel
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
    ref: UUID

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
