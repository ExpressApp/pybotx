from http import HTTPStatus
from typing import Any, Literal
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_fixed

from pybotx import (
    BotXRetryStrategy,
    BotXRetryPolicy,
    BotAccountWithSecret,
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.client.botx_method import BotXMethod, response_exception_thrower
from pybotx.client.exceptions.base import BaseClientError
from pybotx.client.observability import (
    BotXRequestMetadata,
    BotXRequestResult,
    BotXRetryEvent,
)
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class FooBarError(BaseClientError):
    """Test exception."""


class BotXAPIFooBarRequestPayload(UnverifiedPayloadBaseModel):
    baz: int

    @classmethod
    def from_domain(cls, baz: int) -> "BotXAPIFooBarRequestPayload":
        return cls(baz=baz)


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPIFooBarResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class FooBarMethod(BotXMethod):
    status_handlers = {
        403: response_exception_thrower(FooBarError, "FooBar comment"),
    }

    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIFooBarResponsePayload,
            response,
        )


class ObserverSpy:
    def __init__(self) -> None:
        self.start_events: list[BotXRequestMetadata] = []
        self.retry_events: list[tuple[BotXRequestMetadata, BotXRetryEvent]] = []
        self.finish_events: list[tuple[BotXRequestMetadata, BotXRequestResult]] = []

    def on_request_start(self, metadata: BotXRequestMetadata) -> None:
        self.start_events.append(metadata)

    def on_request_retry(
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        self.retry_events.append((metadata, retry_event))

    def on_request_finish(
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        self.finish_events.append((metadata, result))


class TwoAttemptsRetryStrategy(BotXRetryStrategy):
    def build_retrying(
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: tuple[type[BaseException], ...],
        before_sleep: Any,
    ) -> AsyncRetrying:
        return AsyncRetrying(
            stop=stop_after_attempt(2),
            wait=wait_fixed(0.0),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep,
            reraise=True,
        )


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__botx_method__invalid_botx_status_code_error_raised(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(HTTPStatus.METHOD_NOT_ALLOWED),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "failed with code 405" in str(exc.value)
    assert endpoint.called


async def test__botx_method__invalid_json_raises_invalid_botx_response_payload_error(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content='{"invalid": "json',
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXResponsePayloadError) as exc:
        await method.execute(payload)

    # - Assert -
    assert '{"invalid": "json' in str(exc.value)
    assert endpoint.called


async def test__botx_method__invalid_schema_raises_invalid_botx_response_payload_error(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"invalid": "schema"},
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXResponsePayloadError) as exc:
        await method.execute(payload)

    # - Assert -
    assert '{"invalid":"schema"}' in str(exc.value)
    assert endpoint.called


async def test__botx_method__status_handler_called(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(FooBarError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "403" in str(exc.value)
    assert "FooBar comment" in str(exc.value)
    assert endpoint.called


async def test__botx_method__succeed(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@pytest.mark.parametrize(
    "cts_url",
    (
        "http://127.0.0.1",
        "http://localhost",
        "http://cts.ru",
        "https://cts.ru",
        "http://cts.ru:8000",
        "http://cts.ru/foo/bar",
        "http://cts.ru:8000/foo/bar/",
    ),
)
async def test__build_botx_url_with_different_bot_cts_urls(
    bot_id: UUID,
    cts_url: str,
    respx_mock: MockRouter,
    httpx_client: httpx.AsyncClient,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        "/".join(parts.strip("/") for parts in (cts_url, "/foo/bar")),
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    await method.execute(payload)

    # - Assert -
    assert endpoint.called


async def test__botx_method__retries_on_retryable_transport_errors(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    retry_policy = BotXRetryPolicy(
        max_attempts=2,
        initial_delay_seconds=0.0,
        max_delay_seconds=0.0,
        jitter_seconds=0.0,
    )

    call_counter = 0

    def responder(_: httpx.Request) -> httpx.Response:
        nonlocal call_counter
        call_counter += 1
        if call_counter == 1:
            raise httpx.ConnectTimeout("Connection timeout")

        return httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        )

    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(side_effect=responder)

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], retry_policy=retry_policy),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    result = await method.execute(payload)

    # - Assert -
    assert result.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.call_count == 2


async def test__botx_method__retries_on_retryable_status_code_and_succeeds(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    retry_policy = BotXRetryPolicy(
        max_attempts=2,
        initial_delay_seconds=0.0,
        max_delay_seconds=0.0,
        jitter_seconds=0.0,
    )

    call_counter = 0

    def responder(_: httpx.Request) -> httpx.Response:
        nonlocal call_counter
        call_counter += 1
        if call_counter == 1:
            return httpx.Response(HTTPStatus.SERVICE_UNAVAILABLE)

        return httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        )

    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(side_effect=responder)

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], retry_policy=retry_policy),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    result = await method.execute(payload)

    # - Assert -
    assert result.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.call_count == 2


async def test__botx_method__retryable_status_exhausted_returns_original_status_error(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    retry_policy = BotXRetryPolicy(
        max_attempts=2,
        initial_delay_seconds=0.0,
        max_delay_seconds=0.0,
        jitter_seconds=0.0,
    )

    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(
        return_value=httpx.Response(HTTPStatus.SERVICE_UNAVAILABLE),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], retry_policy=retry_policy),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "failed with code 503" in str(exc.value)
    assert endpoint.call_count == 2


async def test__botx_method__without_retry_policy_does_not_retry(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(
        return_value=httpx.Response(HTTPStatus.SERVICE_UNAVAILABLE),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError):
        await method.execute(payload)

    # - Assert -
    assert endpoint.call_count == 1


async def test__botx_method__metrics_and_tracing_are_opt_in_and_report_retry_events(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    call_counter = 0
    metrics_collector = ObserverSpy()
    tracing_collector = ObserverSpy()

    def responder(_: httpx.Request) -> httpx.Response:
        nonlocal call_counter
        call_counter += 1
        if call_counter == 1:
            return httpx.Response(HTTPStatus.SERVICE_UNAVAILABLE)
        return httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        )

    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(side_effect=responder)

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage(
            [bot_account],
            retry_policy=BotXRetryPolicy(
                max_attempts=2,
                initial_delay_seconds=0.0,
                max_delay_seconds=0.0,
                jitter_seconds=0.0,
            ),
            metrics_collector=metrics_collector,
            tracing_collector=tracing_collector,
        ),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    result = await method.execute(payload)

    # - Assert -
    assert result.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.call_count == 2

    assert len(metrics_collector.start_events) == 1
    assert len(metrics_collector.retry_events) == 1
    assert len(metrics_collector.finish_events) == 1
    assert metrics_collector.finish_events[0][1].status_code == HTTPStatus.OK
    assert metrics_collector.finish_events[0][1].error is None

    assert len(tracing_collector.start_events) == 1
    assert len(tracing_collector.retry_events) == 1
    assert len(tracing_collector.finish_events) == 1


async def test__botx_method__custom_retry_strategy_overrides_default_tenacity_setup(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    call_counter = 0

    def responder(_: httpx.Request) -> httpx.Response:
        nonlocal call_counter
        call_counter += 1
        if call_counter == 1:
            return httpx.Response(HTTPStatus.SERVICE_UNAVAILABLE)
        return httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        )

    endpoint = respx_mock.post(f"https://{host}/foo/bar").mock(side_effect=responder)
    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage(
            [bot_account],
            # Policy says one attempt, but strategy forces two attempts.
            retry_policy=BotXRetryPolicy(max_attempts=1),
            retry_strategy=TwoAttemptsRetryStrategy(),
        ),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    result = await method.execute(payload)

    # - Assert -
    assert result.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.call_count == 2
