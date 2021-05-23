"""Mixin for shortcut for smartapp."""

from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.smartapp.post import SmartAppEvent
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.smartapp import SendingSmartApp


class SmartAppMixin:
    """Mixin for shortcut for post smartapp."""

    async def send_smartapp(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        smartapp: SendingSmartApp,
    ) -> UUID:
        """Send command result into chat.

        Arguments:
            credentials: credentials for making request.
            payload: payload for command result.

        Returns:
             ID sent message.
        """
        return await self.call_method(
            SmartAppEvent(**smartapp.dict()),
            credentials=credentials,
        )
