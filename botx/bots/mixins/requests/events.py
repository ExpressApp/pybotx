"""Mixin for shortcut for events resource requests."""
from typing import Optional, List
from uuid import UUID

from botx.models.messages.message import Message, File
from botx.models.entities import Mention
from botx.models.messages.sending.markup import MessageMarkup
from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.events.reply_event import ReplyEvent
from botx.clients.types.message_payload import UpdatePayload, ResultPayload
from botx.clients.types.options import ResultOptions
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.payload import UpdatePayload as SendingUpdatePayload


class EventsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def update_message(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        update: SendingUpdatePayload,
    ) -> None:
        """Change message by it's event id.

        Arguments:
            credentials: credentials that are used for sending message. *sync_id* is
                required for credentials.
            update: update of message content.

        Raises:
            ValueError: raised if sync_id wasn't provided
        """
        if not credentials.sync_id:
            raise ValueError("sync_id is required for message update")

        await self.call_method(
            EditEvent(
                sync_id=credentials.sync_id,
                result=UpdatePayload(
                    body=update.text,
                    keyboard=update.keyboard,
                    bubble=update.bubbles,
                    mentions=update.mentions,
                ),
                file=update.file,
            ),
            credentials=credentials,
        )
    async def reply(
            self: BotXMethodCallProtocol,
            text: str,
            message: Optional[Message] = None,
            *,
            source_sync_id: Optional[UUID] = None,
            credentials: Optional[SendingCredentials] = None,
            file: Optional[File] = None,
            markup: MessageMarkup = MessageMarkup(),
            mentions: Optional[List[Mention]] = None,
            opts: ResultOptions = ResultOptions()
    ) -> None:
        """Change message by it's event id.

        Arguments:
            text: text of message
            message: source message that will replied
            source_sync_id: source message uuid that will replied
            file: attachment file
            markup: markup of sending message
            opts: options of sending message.
            credentials: credentials for making request.

        """
        if (message is None) and (source_sync_id is None or credentials is None):
            raise ValueError("message or source_sync_id with credentials required")

        if message and (source_sync_id or credentials):
            raise ValueError(
                "message and source_sync_id with credentials are incompatible"
            )

        if not text:
            raise ValueError("text can't be empty")

        if message:
            source_sync_id = message.sync_id
            credentials = message.credentials

        await self.call_method(
            ReplyEvent(
                source_sync_id=source_sync_id,
                result=ResultPayload(
                    body=text,
                    keyboard=markup.keyboard,
                    bubble=markup.bubbles,
                    mentions=mentions or [],
                ),
                file=file,
                opts=opts
            ),
            credentials=credentials
        )