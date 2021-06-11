"""Mixin for shortcut for smartapp."""

from typing import Any
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.smartapp.post import SmartAppEvent, SmartAppNotification
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.smartapp import SendingSmartApp, SendingSmartAppNotification


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

    async def send_smartapp_notification(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        smartapp_notification: SendingSmartAppNotification,
    ) -> None:
        """Send unread notifications count."""
        await self.call_method(
            SmartAppNotification(**smartapp_notification.dict()),
            credentials=credentials,
        )
