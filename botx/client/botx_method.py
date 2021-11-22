from contextlib import asynccontextmanager
from json.decoder import JSONDecodeError
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Mapping,
    NoReturn,
    Optional,
    Type,
    TypeVar,
)
from urllib.parse import urljoin
from uuid import UUID

import httpx
from mypy_extensions import Arg
from pydantic import ValidationError, parse_raw_as

from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.callbacks_manager import CallbacksManager
from botx.bot.models.method_callbacks import (
    BotAPIMethodFailedCallback,
    BotXMethodCallback,
)
from botx.client.exceptions.base import BaseClientException
from botx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError
from botx.client.exceptions.http import (
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel

StatusHandler = Callable[[Arg(httpx.Response, "response")], NoReturn]  # noqa: F821
StatusHandlers = Mapping[int, StatusHandler]

CallbackExceptionHandler = Callable[
    [Arg(BotAPIMethodFailedCallback, "callback")],  # noqa: F821
    NoReturn,
]
ErrorCallbackHandlers = Mapping[str, CallbackExceptionHandler]
TBotXAPIModel = TypeVar("TBotXAPIModel", bound=VerifiedPayloadBaseModel)


def response_exception_thrower(
    exc: Type[BaseClientException],
    comment: Optional[str] = None,
) -> StatusHandler:
    def factory(response: httpx.Response) -> NoReturn:
        raise exc.from_response(response, comment)

    return factory


def callback_exception_thrower(
    exc: Type[BaseClientException],
    comment: Optional[str] = None,
) -> CallbackExceptionHandler:  # noqa: F821
    def factory(callback: BotAPIMethodFailedCallback) -> NoReturn:
        raise exc.from_callback(callback, comment)

    return factory


class BotXMethod:
    status_handlers: StatusHandlers = {}
    error_callback_handlers: ErrorCallbackHandlers = {}

    def __init__(
        self,
        sender_bot_id: UUID,
        httpx_client: httpx.AsyncClient,
        bot_accounts_storage: BotAccountsStorage,
        callbacks_manager: Optional[CallbacksManager] = None,
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

    def _verify_and_extract_api_model(
        self,
        model_cls: Type[TBotXAPIModel],
        response: httpx.Response,
    ) -> TBotXAPIModel:
        try:
            return parse_raw_as(model_cls, response.content)
        except (ValidationError, JSONDecodeError) as exc:
            raise InvalidBotXResponsePayloadError(response) from exc

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> httpx.Response:
        response = await self._httpx_client.request(*args, **kwargs)
        await self._raise_for_status(response)

        return response

    @asynccontextmanager
    async def _botx_method_stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[httpx.Response, None]:
        async with self._httpx_client.stream(*args, **kwargs) as response:
            await self._raise_for_status(response)
            yield response

    async def _raise_for_status(self, response: httpx.Response) -> None:
        handler = self.status_handlers.get(response.status_code)
        if handler:
            if not response.is_closed:
                await response.aread()

            handler(response)  # Handler should raise an exception

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if not response.is_closed:
                await response.aread()

            raise InvalidBotXStatusCodeError(exc.response)

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
                raise BotXMethodFailedCallbackReceivedError(callback)

            error_handler(callback)  # Handler should raise an exception

        return callback
