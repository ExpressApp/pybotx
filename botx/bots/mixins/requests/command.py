"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING, cast
from uuid import UUID

from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.types.options import ResultOptions
from botx.clients.types.result_payload import ResultPayload
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433


class CommandRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def send_command_result(
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
    ) -> UUID:
        return await self.call_method(
            CommandResult(
                bot_id=cast(UUID, credentials.bot_id),
                sync_id=cast(UUID, credentials.sync_id),
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )
