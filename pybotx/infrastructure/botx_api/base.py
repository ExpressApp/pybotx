from __future__ import annotations

from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.callback_manager import CallbackManagerPort
from pybotx.domain.ports.http_client import HttpClientPort
from pybotx.infrastructure.botx_api.method_factory import BotXApiMethodFactory
from pybotx.infrastructure.services.users_csv import UsersCsvService


class BotXApiBase:
    def __init__(
        self,
        *,
        http_client: HttpClientPort,
        bot_accounts_storage: BotAccountsStoragePort,
        callbacks_manager: CallbackManagerPort,
        method_factory: BotXApiMethodFactory | None = None,
        users_csv_service: UsersCsvService | None = None,
        default_callback_timeout: float = 60.0,
    ) -> None:
        self._http_client = http_client
        self._bot_accounts_storage = bot_accounts_storage
        self._callbacks_manager = callbacks_manager
        self._method_factory = method_factory or BotXApiMethodFactory(
            http_client=http_client,
            bot_accounts_storage=bot_accounts_storage,
            callbacks_manager=callbacks_manager,
        )
        self._users_csv_service = users_csv_service or UsersCsvService(
            method_factory=self._method_factory,
        )
        self._default_callback_timeout = default_callback_timeout

    async def aclose(self) -> None:
        await self._http_client.aclose()

    def get_http_client(self) -> HttpClientPort:
        return self._http_client

    def get_default_callback_timeout(self) -> float:
        return self._default_callback_timeout
