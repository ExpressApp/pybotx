"""Mixin for shortcut for command resource requests."""

from typing import cast
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.options import ResultPayloadOptions
from botx.models.messages.sending.payload import MessagePayload


class CommandRequestsMixin:
    """Mixin for shortcut for command resource requests."""

    async def send_command_result(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        payload: MessagePayload,
    ) -> UUID:
        """Send command result into chat.

        Arguments:
            credentials: credentials for making request.
            payload: payload for command result.

        Returns:
             ID sent message.
        """
        return await self.call_method(
            CommandResult(
                sync_id=cast(UUID, credentials.sync_id),
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    metadata=payload.metadata,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                    opts=ResultPayloadOptions(
                        silent_response=payload.options.silent_response,
                    ),
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(
                    stealth_mode=payload.options.stealth_mode,
                    notification_opts=payload.options.notifications,
                ),
            ),
            credentials=credentials,
        )
