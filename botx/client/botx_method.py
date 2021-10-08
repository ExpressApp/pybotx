from typing import Any, Awaitable, Callable, Mapping, NoReturn, Optional, Type, TypeVar
from urllib.parse import urljoin
from uuid import UUID

import httpx
from mypy_extensions import Arg
from pydantic import ValidationError

from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.botx_methods_callbacks_manager import BotXMethodsCallbacksManager
from botx.bot.models.botx_method_callbacks import (
    BotXMethodCallback,
    BotXMethodCallbackFailed,
)
from botx.client.exceptions.callbacks import BotXMethodCallbackFailedReceived
from botx.client.exceptions.http import (
    InvalidBotXResponseError,
    InvalidBotXStatusCodeError,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel

StatusHandlers = Mapping[  # noqa: WPS221  (StatusHandler used only in this Mapping)
    int,
    Callable[[Arg(httpx.Response, "response")], NoReturn],  # noqa: F821
]

ErrorCallbackHandlers = (
    Mapping[  # noqa: WPS221  (StatusHandler used only in this Mapping)
        str,
        Callable[[BotXMethodCallbackFailed], NoReturn],
    ]
)
TBotXAPIModel = TypeVar("TBotXAPIModel", bound=VerifiedPayloadBaseModel)


class BotXMethod:
    status_handlers: StatusHandlers = {}
    error_callback_handlers: ErrorCallbackHandlers = {}

    def __init__(
        self,
        sender_bot_id: UUID,
        httpx_client: httpx.AsyncClient,
        bot_accounts_storage: BotAccountsStorage,
        callbacks_manager: Optional[BotXMethodsCallbacksManager] = None,
    ) -> None:
        self._bot_id = sender_bot_id
        self._httpx_client = httpx_client
        self._bot_accounts_storage = bot_accounts_storage
        self._callbacks_manager = callbacks_manager

    # For MyPy checks
    execute: Callable[..., Awaitable[Any]]

    async def execute(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        raise NotImplementedError("You should define `execute` method")

    def _build_url(self, path: str) -> str:
        host = self._bot_accounts_storage.get_host(self._bot_id)
        return urljoin(f"https://{host}", path)

    def _extract_api_model(
        self,
        model_cls: Type[TBotXAPIModel],
        response: httpx.Response,
    ) -> TBotXAPIModel:
        try:
            return model_cls.parse_raw(response.content)
        except ValidationError as exc:
            raise InvalidBotXResponseError(response) from exc

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> httpx.Response:
        response = await self._httpx_client.request(*args, **kwargs)

        handler = self.status_handlers.get(response.status_code)
        if handler:
            handler(response)  # Handler should raise an exception

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise InvalidBotXStatusCodeError(exc.response)

        return response

    async def _process_callback(
        self,
        sync_id: UUID,
        wait_callback: bool,
        callback_timeout: Optional[int],
    ) -> Optional[BotXMethodCallback]:
        assert (
            self._callbacks_manager is not None
        ), "CallbackManager hasn't been passed to this method"

        self._callbacks_manager.create_botx_method_callback(sync_id)

        if not wait_callback:
            return None

        callback = await self._callbacks_manager.wait_botx_method_callback(
            sync_id,
            callback_timeout,
        )

        if callback.status == "error":
            error_handler = self.error_callback_handlers.get(callback.reason)
            if not error_handler:
                raise BotXMethodCallbackFailedReceived(callback)

            error_handler(callback)  # Handler should raise an exception

        return callback
