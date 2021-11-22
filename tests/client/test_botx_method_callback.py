# type: ignore [attr-defined]

import asyncio
import types
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BotShuttignDownError,
    BotXMethodFailedCallbackReceivedError,
    CallbackNotReceivedError,
    HandlerCollector,
    lifespan_wrapper,
)
from botx.client.botx_method import (
    BotXMethod,
    ErrorCallbackHandlers,
    callback_exception_thrower,
)
from botx.client.exceptions.base import BaseClientException
from botx.missing import MissingOptional, Undefined, not_undefined
from tests.client.test_botx_method import (
    BotXAPIFooBarRequestPayload,
    BotXAPIFooBarResponsePayload,
)


class FooBarError(BaseClientException):
    """Test exception."""


class FooBarCallbackMethod(BotXMethod):
    error_callback_handlers: ErrorCallbackHandlers = {
        "foo_bar_error": callback_exception_thrower(
            FooBarError,
            "FooBar comment",
        ),
    }

    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
        wait_callback: bool,
        callback_timeout: MissingOptional[int] = Undefined,
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        api_model = self._verify_and_extract_api_model(
            BotXAPIFooBarResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
        )

        return api_model


async def call_foo_bar(
    self: Bot,
    bot_id: UUID,
    baz: int,
    wait_callback: bool = True,
    callback_timeout: Optional[int] = None,
) -> UUID:
    method = FooBarCallbackMethod(
        bot_id,
        self._httpx_client,
        self._bot_accounts_storage,
        self._callback_manager,
    )

    payload = BotXAPIFooBarRequestPayload.from_domain(baz=baz)
    botx_api_foo_bar = await method.execute(
        payload,
        wait_callback,
        not_undefined(callback_timeout, self.default_callback_timeout),
    )

    return botx_api_foo_bar.to_domain()


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__error_callback_error_handler_called(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "foo_bar_error",
                "errors": [],
                "error_data": {
                    "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
                    "error_description": (
                        "Chat with id 705df263-6bfd-536a-9d51-13524afaab5c not found"
                    ),
                },
            },
        )

        with pytest.raises(FooBarError) as exc:
            await task

    # - Assert -
    assert "foo_bar_error" in str(exc.value)
    assert "FooBar comment" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__error_callback_received(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "quux_error",
                "errors": [],
                "error_data": {
                    "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
                    "error_description": (
                        "Chat with id 705df263-6bfd-536a-9d51-13524afaab5c not found"
                    ),
                },
            },
        )

        with pytest.raises(BotXMethodFailedCallbackReceivedError) as exc:
            await task

    # - Assert -
    assert "failed with" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__cancelled_callback_future_during_shutdown(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    sync_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallbackNotReceivedError):
            await bot.call_foo_bar(bot_id, baz=1, callback_timeout=0)

    # - Assert -
    # This test is considered as passed if no exception was raised
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__callback_received_after_timeout(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    sync_id: UUID,
    loguru_caplog: pytest.LogCaptureFixture,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallbackNotReceivedError) as exc:
            await bot.call_foo_bar(bot_id, baz=1, callback_timeout=0)

        bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": str(sync_id),
                "reason": "quux_error",
                "errors": [],
                "error_data": {
                    "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
                    "error_description": (
                        "Chat with id 705df263-6bfd-536a-9d51-13524afaab5c not found"
                    ),
                },
            },
        )

    # - Assert -
    assert "hasn't been received" in str(exc.value)
    assert "don't wait callback" in loguru_caplog.text
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__dont_wait_for_callback(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    sync_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        foo_bar = await bot.call_foo_bar(bot_id, baz=1, wait_callback=False)

    # - Assert -
    assert foo_bar == sync_id
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__pending_callback_future_during_shutdown(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    sync_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # HTTP-client should have time to make request

    with pytest.raises(BotShuttignDownError) as exc:
        await task

    # - Assert -
    assert str(sync_id) in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method_callback__callback_successful_received(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    sync_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": str(sync_id),
                "result": {},
            },
        )

    # - Assert -
    assert await task == sync_id
    assert endpoint.called
