"""Definition for mixin that defines BotX API methods."""
from typing import cast
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.events.edit_event import EditEvent, UpdatePayload
from botx.models import sending


class EventsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def update_message(
        self: BotXMethodCallProtocol,
        credentials: sending.SendingCredentials,
        update: sending.UpdatePayload,
    ) -> None:
        """Change message by it's event id.

        Arguments:
            credentials: credentials that are used for sending message. *sync_id* is
                required for credentials.
            update: update of message content.
        """
        return await self.call_method(
            EditEvent(
                sync_id=cast(UUID, credentials.sync_id),
                result=UpdatePayload(
                    body=update.text,
                    keyboard=update.keyboard,
                    bubble=update.bubbles,
                    mentions=update.mentions,
                ),
            ),
            credentials=credentials,
        )
