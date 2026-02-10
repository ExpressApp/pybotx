from __future__ import annotations

from typing import Any

from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.callback_manager import CallbackManagerPort
from pybotx.domain.ports.http_client import HttpClientPort


class BotXApiMethodFactory:
    def __init__(
        self,
        *,
        http_client: HttpClientPort,
        bot_accounts_storage: BotAccountsStoragePort,
        callbacks_manager: CallbackManagerPort,
    ) -> None:
        self._http_client = http_client
        self._bot_accounts_storage = bot_accounts_storage
        self._callbacks_manager = callbacks_manager

    def build(
        self,
        method_cls: type[Any],
        *,
        bot_id: Any,
        with_callbacks: bool = False,
    ) -> Any:
        if with_callbacks:
            return method_cls(
                bot_id,
                self._http_client,
                self._bot_accounts_storage,
                self._callbacks_manager,
            )
        return method_cls(
            bot_id,
            self._http_client,
            self._bot_accounts_storage,
        )


__all__ = ("BotXApiMethodFactory",)
