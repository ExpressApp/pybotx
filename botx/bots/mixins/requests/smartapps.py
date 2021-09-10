"""Mixin for shortcut for smartapp."""

from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.smartapps.smartapp_event import SmartAppEvent
from botx.clients.methods.v3.smartapps.smartapp_notification import SmartAppNotification
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.smartapps import SendingSmartAppEvent, SendingSmartAppNotification


class SmartAppMixin:
    """Mixin for shortcut for smartapp methods."""

    async def send_smartapp_event(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        smartapp_event: SendingSmartAppEvent,
    ) -> UUID:
        """Send smartapp event into chat.

        Arguments:
            credentials: credentials for making request.
            smartapp_event: SmartpApp event.

        Returns:
             ID sent message.
        """
        return await self.call_method(
            SmartAppEvent(
                ref=smartapp_event.ref,
                smartapp_id=smartapp_event.smartapp_id,
                data=smartapp_event.data,
                opts=smartapp_event.opts,
                smartapp_api_version=smartapp_event.smartapp_api_version,
                group_chat_id=smartapp_event.group_chat_id,
                files=smartapp_event.files,
                async_files=smartapp_event.async_files,
            ),
            credentials=credentials,
        )

    async def send_smartapp_notification(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        smartapp_notification: SendingSmartAppNotification,
    ) -> None:
        """Send smartapp notification into chat.

        Arguments:
            credentials: credentials for making request.
            smartapp_notification: Smartapp notification.
        """
        await self.call_method(
            SmartAppNotification(
                group_chat_id=smartapp_notification.group_chat_id,
                smartapp_counter=smartapp_notification.smartapp_counter,
                opts=smartapp_notification.opts,
                smartapp_api_version=smartapp_notification.smartapp_api_version,
            ),
            credentials=credentials,
        )
