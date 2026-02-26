import json
import time
from contextlib import asynccontextmanager
from json.decoder import JSONDecodeError
from typing import (
    Any,
    NoReturn,
    TypeVar,
)
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from uuid import UUID

import httpx
from mypy_extensions import Arg
from tenacity import (
    RetryCallState,
)

from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.bot.callbacks.callback_manager import CallbackManager
from pybotx.client.exceptions.base import BaseClientError
from pybotx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError
from pybotx.client.exceptions.http import (
    InvalidBotXResponseError,
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from pybotx.client.http_config import TenacityRetryStrategy
from pybotx.client.observability import (
    BotXRequestMetadata,
    BotXRequestObserver,
    BotXRequestResult,
    BotXRetryEvent,
)
from pybotx.logger import logger, pformat_jsonable_obj, trim_file_data_in_outgoing_json
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.method_callbacks import (
    BotAPIMethodFailedCallback,
    BotXMethodCallback,
)
from pydantic import ValidationError

StatusHandler = Callable[[Arg(httpx.Response, "response")], NoReturn]  # noqa: F821
StatusHandlers = Mapping[int, StatusHandler]

CallbackExceptionHandler = Callable[
    [Arg(BotAPIMethodFailedCallback, "callback")],  # noqa: F821
    NoReturn,
]
ErrorCallbackHandlers = Mapping[str, CallbackExceptionHandler]
TBotXAPIModel = TypeVar("TBotXAPIModel", bound=VerifiedPayloadBaseModel)
RequestCall = Callable[..., Awaitable[httpx.Response]]
RequestDecorator = Callable[[RequestCall], RequestCall]


class RetryableBotXStatusCodeError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        super().__init__(response.status_code)
        self.response = response


def response_exception_thrower(
    exc: type[BaseClientError],
    comment: str | None = None,
) -> StatusHandler:
    def factory(response: httpx.Response) -> NoReturn:
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
        httpx_client: httpx.AsyncClient,
        bot_accounts_storage: BotAccountsStorage,
        callbacks_manager: CallbackManager | None = None,
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
        model_cls: type[TBotXAPIModel],
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
            api_model = model_cls.model_validate(raw_model)
        except ValidationError as validation_exc:
            raise InvalidBotXResponsePayloadError(response) from validation_exc

        return api_model

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> httpx.Response:
        self._log_outgoing_request(*args, **kwargs)

        method, url = args
        request = self._decorate_request(
            self._httpx_client.request,
            method=method,
            url=url,
        )
        response = await request(*args, **kwargs)
        await self._raise_for_status(response)

        return response

    @asynccontextmanager
    async def _botx_method_stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[httpx.Response, None]:
        self._log_outgoing_request(*args, **kwargs)

        method, url = args
        stream_request = self._decorate_request(
            self._streaming_request,
            method=method,
            url=url,
        )
        response = await stream_request(*args, **kwargs)
        try:
            await self._raise_for_status(response)
            yield response
        finally:
            await response.aclose()

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

    async def _streaming_request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        method, url = args
        request = self._httpx_client.build_request(method, url, **kwargs)
        return await self._httpx_client.send(request, stream=True)

    async def _retryable_request_call(
        self,
        request_call: RequestCall,
        retryable_status_codes: frozenset[int],
        *args: Any,
        **kwargs: Any,
    ) -> httpx.Response:
        response = await request_call(*args, **kwargs)
        if response.status_code not in retryable_status_codes:
            return response

        if not response.is_closed:
            await response.aread()
        await response.aclose()
        raise RetryableBotXStatusCodeError(response)

    def _decorate_request(
        self,
        request_call: RequestCall,
        *,
        method: str,
        url: str,
    ) -> RequestCall:
        decorated = request_call
        for decorator in self._request_decorators(method=method, url=url):
            decorated = decorator(decorated)
        return decorated

    def _request_decorators(self, *, method: str, url: str) -> list[RequestDecorator]:
        decorators: list[RequestDecorator] = []
        retry_policy = self._bot_accounts_storage.get_retry_policy()
        if retry_policy is not None:
            decorators.append(self._build_retry_decorator(method=method, url=url))

        observers = tuple(self._bot_accounts_storage.iter_request_observers())
        if observers:
            decorators.append(
                self._build_observability_decorator(
                    method=method,
                    url=url,
                    observers=observers,
                ),
            )

        return decorators

    def _build_observability_decorator(
        self,
        *,
        method: str,
        url: str,
        observers: tuple[BotXRequestObserver, ...],
    ) -> RequestDecorator:
        metadata = BotXRequestMetadata(method=method, url=url)

        def decorator(request_call: RequestCall) -> RequestCall:
            async def wrapped(*args: Any, **kwargs: Any) -> httpx.Response:
                started_at = time.perf_counter()
                self._notify_request_start(observers, metadata)
                try:
                    response = await request_call(*args, **kwargs)
                except Exception as exc:
                    duration_ms = int((time.perf_counter() - started_at) * 1000)
                    status_code = (
                        exc.response.status_code
                        if isinstance(exc, InvalidBotXResponseError)
                        else None
                    )
                    self._notify_request_finish(
                        observers,
                        metadata,
                        BotXRequestResult(
                            status_code=status_code,
                            duration_ms=duration_ms,
                            error=exc,
                        ),
                    )
                    raise

                duration_ms = int((time.perf_counter() - started_at) * 1000)
                self._notify_request_finish(
                    observers,
                    metadata,
                    BotXRequestResult(
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                    ),
                )
                return response

            return wrapped

        return decorator

    def _build_retry_decorator(self, *, method: str, url: str) -> RequestDecorator:
        retry_policy = self._bot_accounts_storage.get_retry_policy()
        assert retry_policy is not None
        retry_strategy = (
            self._bot_accounts_storage.get_retry_strategy() or TenacityRetryStrategy()
        )
        retry_exceptions = (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
            RetryableBotXStatusCodeError,
        )
        observers = tuple(self._bot_accounts_storage.iter_request_observers())
        metadata = BotXRequestMetadata(method=method, url=url)

        def decorator(request_call: RequestCall) -> RequestCall:
            async def wrapped(*args: Any, **kwargs: Any) -> httpx.Response:
                retrying = retry_strategy.build_retrying(
                    retry_policy=retry_policy,
                    retry_exceptions=retry_exceptions,
                    before_sleep=self._build_before_sleep_logger(
                        method=method,
                        url=url,
                        max_attempts=retry_policy.max_attempts,
                        metadata=metadata,
                        observers=observers,
                    ),
                )
                try:
                    return await retrying(
                        self._retryable_request_call,
                        request_call,
                        retry_policy.retryable_status_codes,
                        *args,
                        **kwargs,
                    )
                except RetryableBotXStatusCodeError as exc:
                    return exc.response

            return wrapped

        return decorator

    def _build_before_sleep_logger(
        self,
        *,
        method: str,
        url: str,
        max_attempts: int,
        metadata: BotXRequestMetadata,
        observers: tuple[BotXRequestObserver, ...],
    ) -> Callable[[RetryCallState], None]:
        def callback(retry_state: RetryCallState) -> None:
            sleep_seconds = (
                retry_state.next_action.sleep
                if retry_state.next_action is not None
                else 0.0
            )
            reason = self._format_retry_reason(retry_state)
            logger.warning(
                "Retrying BotX request {method} {url}. "
                "Attempt {attempt}/{max_attempts}. "
                "Sleeping {sleep_seconds:.3f}s. "
                "Reason: {reason}",
                method=method,
                url=url,
                attempt=retry_state.attempt_number,
                max_attempts=max_attempts,
                sleep_seconds=sleep_seconds,
                reason=reason,
            )
            retry_event = BotXRetryEvent(
                attempt=retry_state.attempt_number,
                max_attempts=max_attempts,
                sleep_seconds=sleep_seconds,
                reason=reason,
            )
            self._notify_request_retry(
                observers=observers,
                metadata=metadata,
                retry_event=retry_event,
            )

        return callback

    def _format_retry_reason(self, retry_state: RetryCallState) -> str:
        if retry_state.outcome is None or not retry_state.outcome.failed:
            return "unknown"

        exc = retry_state.outcome.exception()
        if exc is None:
            return "unknown"
        if isinstance(exc, RetryableBotXStatusCodeError):
            return f"status_code={exc.response.status_code}"
        return f"{type(exc).__name__}: {exc}"

    def _notify_request_start(
        self,
        observers: tuple[BotXRequestObserver, ...],
        metadata: BotXRequestMetadata,
    ) -> None:
        for observer in observers:
            try:
                observer.on_request_start(metadata)
            except Exception:
                logger.opt(exception=True).warning(
                    "Request observer failed in on_request_start",
                )

    def _notify_request_retry(
        self,
        observers: tuple[BotXRequestObserver, ...],
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        for observer in observers:
            try:
                observer.on_request_retry(metadata, retry_event)
            except Exception:
                logger.opt(exception=True).warning(
                    "Request observer failed in on_request_retry",
                )

    def _notify_request_finish(
        self,
        observers: tuple[BotXRequestObserver, ...],
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        for observer in observers:
            try:
                observer.on_request_finish(metadata, result)
            except Exception:
                logger.opt(exception=True).warning(
                    "Request observer failed in on_request_finish",
                )

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
