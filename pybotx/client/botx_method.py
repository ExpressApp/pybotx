import json
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
from uuid import UUID

import httpx
from mypy_extensions import Arg
from pydantic import ValidationError, parse_obj_as

from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.bot.callbacks.callback_manager import CallbackManager
from pybotx.client.exceptions.base import BaseClientError
from pybotx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError
from pybotx.client.exceptions.http import (
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from pybotx.logger import logger, pformat_jsonable_obj, trim_file_data_in_outgoing_json
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.method_callbacks import (
    BotAPIMethodFailedCallback,
    BotXMethodCallback,
)

StatusHandler = Callable[[Arg(httpx.Response, "response")], NoReturn]  # noqa: F821
StatusHandlers = Mapping[int, StatusHandler]

CallbackExceptionHandler = Callable[
    [Arg(BotAPIMethodFailedCallback, "callback")],  # noqa: F821
    NoReturn,
]
ErrorCallbackHandlers = Mapping[str, CallbackExceptionHandler]
TBotXAPIModel = TypeVar("TBotXAPIModel", bound=VerifiedPayloadBaseModel)


def response_exception_thrower(
    exc: Type[BaseClientError],
    comment: Optional[str] = None,
) -> StatusHandler:
    def factory(response: httpx.Response) -> NoReturn:
        raise exc.from_response(response, comment)

    return factory


def callback_exception_thrower(
    exc: Type[BaseClientError],
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
        callbacks_manager: Optional[CallbackManager] = None,
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
        cts_url = self._bot_accounts_storage.get_cts_url(self._bot_id)
        return "/".join(part.strip("/") for part in (cts_url, path))

    def _verify_and_extract_api_model(
        self,
        model_cls: Type[TBotXAPIModel],
        response: httpx.Response,
    ) -> TBotXAPIModel:
        try:
            raw_model = json.loads(response.content)
        except JSONDecodeError as decoding_exc:
            raise InvalidBotXResponsePayloadError(response) from decoding_exc

        logger.opt(lazy=True).debug(
            "Got response from pybotx: {json}",
            json=lambda: pformat_jsonable_obj(raw_model),
        )

        try:
            api_model = parse_obj_as(model_cls, raw_model)
        except ValidationError as validation_exc:
            raise InvalidBotXResponsePayloadError(response) from validation_exc

        return api_model

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> httpx.Response:
        self._log_outgoing_request(*args, **kwargs)

        response = await self._httpx_client.request(*args, **kwargs)
        await self._raise_for_status(response)

        return response

    @asynccontextmanager
    async def _botx_method_stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[httpx.Response, None]:
        self._log_outgoing_request(*args, **kwargs)

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
        callback_timeout: Optional[float],
        default_callback_timeout: float,
    ) -> Optional[BotXMethodCallback]:
        assert (
            self._callbacks_manager is not None
        ), "CallbackManager hasn't been passed to this method"

        await self._callbacks_manager.create_botx_method_callback(sync_id)

        if callback_timeout is None:
            callback_timeout = default_callback_timeout

        if not wait_callback:
            self._callbacks_manager.setup_callback_timeout_alarm(
                sync_id,
                callback_timeout,
            )
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

    def _log_outgoing_request(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        method, url = args
        query_params = kwargs.get("params")
        json_body = kwargs.get("json")

        log_template = "Performing request to BotX:\n{method} {url}"
        if query_params:
            log_template += "\nquery: {params}"
        if json_body is not None:
            log_template += "\njson: {json}"

        logger.opt(lazy=True).debug(
            log_template,
            method=lambda: method,  # If `lazy` enabled, all kwargs should be callable
            url=lambda: url,  # If `lazy` enabled, all kwargs should be callable
            params=lambda: pformat_jsonable_obj(query_params),
            json=lambda: pformat_jsonable_obj(
                trim_file_data_in_outgoing_json(json_body),
            ),
        )
