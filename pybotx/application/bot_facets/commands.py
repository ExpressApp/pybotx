from __future__ import annotations

from asyncio import Task
from uuid import UUID

from pybotx.domain.models.commands import BotCommand
from pybotx.domain.models.method_callbacks import BotXMethodCallback
from pybotx.domain.models.status import BotMenu, StatusRecipient
from pybotx.domain.models.sync_smartapp_event import SyncSmartAppEventResponse
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent


class BotCommandsMixin:
    def async_execute_bot_command(
        self,
        bot_command: BotCommand,
    ) -> "Task[None]":
        # raise UnknownBotAccountError if no bot account with this bot_id.
        self._bot_accounts_storage.ensure_bot_id_exists(bot_command.bot.id)

        return self._handler_collector.async_handle_bot_command(self, bot_command)

    async def sync_execute_smartapp_event(
        self,
        smartapp_event: SmartAppEvent,
    ) -> SyncSmartAppEventResponse:
        self._bot_accounts_storage.ensure_bot_id_exists(smartapp_event.bot.id)
        return await self._handler_collector.handle_sync_smartapp_event(
            self,
            smartapp_event,
        )

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu:
        # raise UnknownBotAccountError if no bot account with this bot_id.
        self._bot_accounts_storage.ensure_bot_id_exists(status_recipient.bot_id)

        return await self._handler_collector.get_bot_menu(status_recipient, self)

    async def set_botx_method_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        await self._callbacks_manager.set_botx_method_callback_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> BotXMethodCallback:
        timeout = self._callbacks_manager.cancel_callback_timeout_alarm(
            sync_id,
            return_remaining_time=True,
        )

        return await self._callbacks_manager.wait_botx_method_callback(sync_id, timeout)
