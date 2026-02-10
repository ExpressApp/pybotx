from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from types import SimpleNamespace
from pybotx.application.bot_facets import (
    BotBotsApiMixin,
    BotChatsMixin,
    BotCommandsMixin,
    BotEventsMixin,
    BotFilesMixin,
    BotLifecycleMixin,
    BotMetricsMixin,
    BotNotificationsMixin,
    BotOpenIdMixin,
    BotSmartAppsMixin,
    BotStickersMixin,
    BotUsersMixin,
    BotWidgetsMixin,
)
from pybotx.application.handler import Middleware
from pybotx.application.handler_collector import HandlerCollector
from pybotx.application.middlewares.exception_middleware import ExceptionHandlersDict
from pybotx.application.request_verifier import RequestVerifier
from pybotx.domain.converters import optional_sequence_to_list
from pybotx.domain.constants import STICKER_PACKS_PER_PAGE
from pybotx.domain.logger import logger
from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.botx_api import BotXApiPort
from pybotx.domain.ports.callback_manager import CallbackManagerPort
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort


class Bot(
    BotCommandsMixin,
    BotLifecycleMixin,
    BotBotsApiMixin,
    BotNotificationsMixin,
    BotEventsMixin,
    BotChatsMixin,
    BotUsersMixin,
    BotWidgetsMixin,
    BotSmartAppsMixin,
    BotStickersMixin,
    BotFilesMixin,
    BotOpenIdMixin,
    BotMetricsMixin,
):
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        bot_accounts_storage: BotAccountsStoragePort,
        callbacks_manager: CallbackManagerPort,
        botx_api: BotXApiPort,
        request_verifier: RequestVerifier,
        widget_state_store: WidgetStateStorePort | None = None,
        middlewares: Sequence[Middleware] | None = None,
        exception_handlers: ExceptionHandlersDict | None = None,
    ) -> None:
        if not collectors:
            logger.warning("Bot has no connected collectors")

        middlewares = optional_sequence_to_list(middlewares)
        self._handler_collector = self._build_main_collector(
            collectors,
            middlewares,
            exception_handlers,
        )

        self._bot_accounts_storage = bot_accounts_storage
        if not list(self._bot_accounts_storage.iter_bot_accounts()):
            logger.warning("Bot has no bot accounts")
        self._callbacks_manager = callbacks_manager
        self._botx_api = botx_api
        self._request_verifier = request_verifier
        self._widget_state_store = widget_state_store

        self.state: SimpleNamespace = SimpleNamespace()

    def _verify_request(
        self,
        headers: Mapping[str, str] | None,
        *,
        trusted_issuers: set[str] | None = None,
    ) -> None:
        self._request_verifier.verify(headers, trusted_issuers=trusted_issuers)

    def verify_request(
        self,
        headers: Mapping[str, str] | None,
        *,
        trusted_issuers: set[str] | None = None,
    ) -> None:
        self._verify_request(headers, trusted_issuers=trusted_issuers)

    @staticmethod
    def _is_v2_payload(token_payload: Mapping[str, Any]) -> bool:
        return RequestVerifier._is_v2_payload(token_payload)

    def _verify_request_v2(
        self,
        token: str,
        token_payload: Mapping[str, Any],
        decode_algorithms: Sequence[str],
    ) -> None:
        self._request_verifier._verify_v2(token, token_payload, decode_algorithms)

    def _verify_request_v1(
        self,
        token: str,
        token_payload: Mapping[str, Any],
        decode_algorithms: Sequence[str],
        trusted_issuers: set[str] | None,
    ) -> None:
        self._request_verifier._verify_v1(
            token,
            token_payload,
            decode_algorithms,
            trusted_issuers=trusted_issuers,
        )

    @staticmethod
    def _build_main_collector(
        collectors: Sequence[HandlerCollector],
        middlewares: list[Middleware],
        exception_handlers: ExceptionHandlersDict | None = None,
    ) -> HandlerCollector:
        main_collector = HandlerCollector(middlewares=middlewares)
        main_collector.insert_exception_middleware(exception_handlers)
        main_collector.include(*collectors)

        return main_collector
