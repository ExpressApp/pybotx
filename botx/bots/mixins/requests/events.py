"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING

from botx.clients.methods.v3.events.edit_event import EditEvent, UpdatePayload
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433


class EventsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def update_message(
        self: "Bot",
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
