import json
from contextlib import asynccontextmanager
from json.decoder import JSONDecodeError
from typing import (
    Any,
    NoReturn,
    TypeVar,
)
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from uuid import UUID

from mypy_extensions import Arg

from pybotx.domain.errors import TransportError
from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.callback_manager import CallbackManagerPort
from pybotx.domain.ports.http_client import (
    HttpClientError,
    HttpClientPort,
    HttpRequest,
    HttpResponse,
    HttpStatusError,
)
from pybotx.infrastructure.client.exceptions.base import BaseClientError
from pybotx.infrastructure.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError
from pybotx.infrastructure.client.exceptions.http import (
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from pybotx.domain.logger import logger, pformat_jsonable_obj, trim_file_data_in_outgoing_json
from pybotx.domain.models.api_base import VerifiedPayloadBaseModel
from pybotx.infrastructure.contracts.method_callbacks import (
    BotAPIMethodFailedCallback,
    BotXMethodCallback,
)
from pydantic import ValidationError

StatusHandler = Callable[[Arg(HttpResponse, "response")], NoReturn]  # noqa: F821
StatusHandlers = Mapping[int, StatusHandler]

CallbackExceptionHandler = Callable[
    [Arg(BotAPIMethodFailedCallback, "callback")],  # noqa: F821
    NoReturn,
]
ErrorCallbackHandlers = Mapping[str, CallbackExceptionHandler]
TBotXAPIModel = TypeVar("TBotXAPIModel", bound=VerifiedPayloadBaseModel)


def response_exception_thrower(
    exc: type[BaseClientError],
    comment: str | None = None,
) -> StatusHandler:
    def factory(response: HttpResponse) -> NoReturn:
        raise exc.from_response(response, comment)

    return factory


def callback_exception_thrower(
    exc: type[BaseClientError],
    comment: str | None = None,
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
        http_client: HttpClientPort,
        bot_accounts_storage: BotAccountsStoragePort,
        callbacks_manager: CallbackManagerPort | None = None,
    ) -> None:
        self._bot_id = sender_bot_id
        self._http_client = http_client
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
        model_cls: type[TBotXAPIModel],
        response: HttpResponse,
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
            api_model = model_cls.model_validate(raw_model)
        except ValidationError as validation_exc:
            raise InvalidBotXResponsePayloadError(response) from validation_exc

        return api_model

    def _build_request(self, method: str, url: str, **kwargs: Any) -> HttpRequest:
        return HttpRequest(
            method=method,
            url=str(url),
            headers=kwargs.get("headers"),
            params=kwargs.get("params"),
            json=kwargs.get("json"),
            data=kwargs.get("data"),
            files=kwargs.get("files"),
            timeout=kwargs.get("timeout"),
        )

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> HttpResponse:
        method, url = args
        request = self._build_request(method, url, **kwargs)
        self._log_outgoing_request(request)

        try:
            response = await self._http_client.send(request)
        except HttpClientError as exc:
            raise TransportError(str(exc)) from exc
        await self._raise_for_status(response)

        return response

    @asynccontextmanager
    async def _botx_method_stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[HttpResponse, None]:
        method, url = args
        request = self._build_request(method, url, **kwargs)
        self._log_outgoing_request(request)

        try:
            async with self._http_client.stream(request) as response:
                await self._raise_for_status(response)
                yield response
        except HttpClientError as exc:
            raise TransportError(str(exc)) from exc

    async def _raise_for_status(self, response: HttpResponse) -> None:
        handler = self.status_handlers.get(response.status_code)
        if handler:
            if not response.is_closed:
                await response.read()

            handler(response)  # Handler should raise an exception

        try:
            response.raise_for_status()
        except HttpStatusError as exc:
            if not response.is_closed:
                await response.read()

            raise InvalidBotXStatusCodeError(exc.response)

    async def _process_callback(
        self,
        sync_id: UUID,
        wait_callback: bool,
        callback_timeout: float | None,
        default_callback_timeout: float,
    ) -> BotXMethodCallback | None:
        assert self._callbacks_manager is not None, (
            "CallbackManager hasn't been passed to this method"
        )

        self._callbacks_manager.register_expected_callback(sync_id)
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

    def _log_outgoing_request(self, request: HttpRequest) -> None:
        method = request.method
        url = request.url
        query_params = request.params
        json_body = request.json

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
