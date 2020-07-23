"""Mixin for shortcut for events resource requests."""

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.types.message_payload import UpdatePayload
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
            ),
            credentials=credentials,
        )
