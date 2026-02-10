from __future__ import annotations

from collections.abc import Iterator

from pybotx.domain.auth import BotXAuthVersion
from pybotx.domain.errors import InvalidBotAccountError, TransportError
from pybotx.domain.logger import logger
from pybotx.domain.models.bot_account import BotAccountWithSecret


class BotLifecycleMixin:
    @property
    def bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._bot_accounts_storage.iter_bot_accounts()

    async def fetch_tokens(self) -> None:
        if self._bot_accounts_storage.get_auth_version() != BotXAuthVersion.V1:
            return
        for bot_account in self.bot_accounts:
            try:
                token = await self.get_token(bot_id=bot_account.id)
            except (InvalidBotAccountError, TransportError):
                logger.opt(exception=True).warning(
                    "Can't get token for bot account: "
                    f"host - {bot_account.host}, bot_id - {bot_account.id}",
                )
                continue

            self._bot_accounts_storage.set_token(bot_account.id, token)

    async def startup(self, *, fetch_tokens: bool = True) -> None:
        if fetch_tokens:
            await self.fetch_tokens()

    async def shutdown(self) -> None:
        await self._callbacks_manager.stop_callbacks_waiting()
        await self._handler_collector.wait_active_tasks()
        await self._botx_api.aclose()
