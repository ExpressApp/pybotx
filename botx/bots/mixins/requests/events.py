"""Mixin for shortcut for events resource requests."""
from typing import List, Optional
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.events.reply_event import ReplyEvent
from botx.clients.types.message_payload import ResultPayload, UpdatePayload
from botx.clients.types.options import ResultOptions
from botx.models.entities import Mention
from botx.models.messages.message import File
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.markup import MessageMarkup
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
                    metadata=update.metadata,
                    keyboard=update.keyboard,
                    bubble=update.bubbles,
                    mentions=update.mentions,
                ),
                file=update.file,
            ),
            credentials=credentials,
        )

    async def reply(  # noqa: WPS211
        self: BotXMethodCallProtocol,
        source_sync_id: UUID,
        credentials: SendingCredentials,
        text: str = "",
        *,
        file: Optional[File] = None,
        markup: Optional[MessageMarkup] = None,
        mentions: Optional[List[Mention]] = None,
        opts: Optional[ResultOptions] = None,
    ) -> None:
        """Reply on message by source_sync_id.

        Arguments:
            text: text of message.
            source_sync_id: source message uuid that will replied.
            file: attachment file.
            markup: markup of sending message.
            opts: options of sending message.
            credentials: credentials for making request.
            mentions: mentions in message.

        Raises:
            ValueError: empty text.
        """
        if not (text or file or mentions):
            raise ValueError("text or file or mention required")

        await self.call_method(
            ReplyEvent(
                source_sync_id=source_sync_id,
                result=ResultPayload(
                    body=text,
                    keyboard=markup.keyboard if markup else [],
                    bubble=markup.bubbles if markup else [],
                    mentions=mentions or [],
                ),
                file=file,
                opts=opts or ResultOptions(),
            ),
            credentials=credentials,
        )
