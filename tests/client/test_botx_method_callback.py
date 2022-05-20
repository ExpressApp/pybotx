# type: ignore [attr-defined]

import asyncio
import types
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotShuttingDownError,
    BotXMethodCallbackNotFoundError,
    BotXMethodFailedCallbackReceivedError,
    CallbackNotReceivedError,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.bot.callbacks.callback_memory_repo import CallbackMemoryRepo
from pybotx.client.botx_method import (
    BotXMethod,
    ErrorCallbackHandlers,
    callback_exception_thrower,
)
from pybotx.client.exceptions.base import BaseClientError
from pybotx.models.method_callbacks import BotAPIMethodSuccessfulCallback
from tests.client.test_botx_method import (
    BotXAPIFooBarRequestPayload,
    BotXAPIFooBarResponsePayload,
)


class FooBarError(BaseClientError):
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
        callback_timeout: Optional[float],
        default_callback_timeout: float,
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
            default_callback_timeout,
        )

        return api_model


async def call_foo_bar(
    self: Bot,
    bot_id: UUID,
    baz: int,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> UUID:
    method = FooBarCallbackMethod(
        bot_id,
        self._httpx_client,
        self._bot_accounts_storage,
        self._callbacks_manager,
    )

    payload = BotXAPIFooBarRequestPayload.from_domain(baz=baz)
    botx_api_foo_bar = await method.execute(
        payload,
        wait_callback,
        callback_timeout,
        self._default_callback_timeout,
    )
    return botx_api_foo_bar.to_domain()


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__botx_method_callback__callback_not_found(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(BotXMethodCallbackNotFoundError) as exc:
            await bot.set_raw_botx_method_result(
                {
                    "status": "error",
                    "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                    "reason": "chat_not_found",
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
    assert "Callback `21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3` doesn't exist" in str(
        exc.value,
    )


async def test__botx_method_callback__error_callback_error_handler_called(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
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


async def test__botx_method_callback__error_callback_received(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
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


async def test__botx_method_callback__cancelled_callback_future_during_shutdown(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallbackNotReceivedError) as exc:
            await bot.call_foo_bar(bot_id, baz=1, callback_timeout=0)

    # - Assert -
    assert "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3" in str(exc.value)
    assert endpoint.called


async def test__botx_method_callback__callback_received_after_timeout(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallbackNotReceivedError) as not_received_exc:
            await bot.call_foo_bar(bot_id, baz=1, callback_timeout=0)

        with pytest.raises(BotXMethodCallbackNotFoundError) as not_found_exc:
            await bot.set_raw_botx_method_result(
                {
                    "status": "error",
                    "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
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
    assert "hasn't been received" in str(not_received_exc.value)
    assert "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3" in str(not_found_exc.value)
    assert endpoint.called


async def test__botx_method_callback__dont_wait_for_callback(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        foo_bar = await bot.call_foo_bar(bot_id, baz=1, wait_callback=False)

    # - Assert -
    assert foo_bar == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__botx_method_callback__pending_callback_future_during_shutdown(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

    with pytest.raises(BotShuttingDownError) as exc:
        await task

    # - Assert -
    assert "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3" in str(exc.value)
    assert endpoint.called


async def test__botx_method_callback__callback_successful_received(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert await task == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__botx_method_callback__callback_successful_received_with_custom_repo(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        callback_repo=CallbackMemoryRepo(),
    )

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert await task == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__botx_method_callback__bot_wait_callback_before_its_receiving(
    respx_mock: MockRouter,
    httpx_client: httpx.AsyncClient,
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        task = asyncio.create_task(bot.wait_botx_method_callback(foo_bar))

        # Return control to event loop
        await asyncio.sleep(0)

        await bot.set_raw_botx_method_result(
            {
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "status": "ok",
                "result": {},
            },
        )

        callback = await task

    # - Assert -
    assert callback == BotAPIMethodSuccessfulCallback(
        sync_id=foo_bar,
        status="ok",
        result={},
    )
    assert endpoint.called


async def test__botx_method_callback__bot_wait_callback_after_its_receiving(
    respx_mock: MockRouter,
    httpx_client: httpx.AsyncClient,
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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

        await bot.set_raw_botx_method_result(
            {
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "status": "ok",
                "result": {},
            },
        )

        callback = await bot.wait_botx_method_callback(foo_bar)

    # - Assert -
    assert callback == BotAPIMethodSuccessfulCallback(
        sync_id=foo_bar,
        status="ok",
        result={},
    )
    assert endpoint.called


async def test__botx_method_callback__bot_dont_wait_received_callback(
    respx_mock: MockRouter,
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
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
        await bot.call_foo_bar(bot_id, baz=1, callback_timeout=0, wait_callback=False)

        # Return control to event loop
        await asyncio.sleep(0)

        await bot.set_raw_botx_method_result(
            {
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "status": "ok",
                "result": {},
            },
        )

    # - Assert -
    assert (
        "Callback `21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3` wasn't waited"
        in loguru_caplog.text
    )
    assert endpoint.called


async def test__botx_method_callback__bot_wait_already_waited_callback(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.call_foo_bar(bot_id, baz=1),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

        foo_bar = await task

        with pytest.raises(BotXMethodCallbackNotFoundError) as exc:
            await bot.wait_botx_method_callback(foo_bar)

    # - Assert -
    assert foo_bar == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called

    assert "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3" in str(exc.value)
    assert "doesn't exist or already waited" in str(exc.value)


async def test__botx_method_callback__bot_wait_timeouted_callback(
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
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    built_bot.call_foo_bar = types.MethodType(call_foo_bar, built_bot)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        foo_bar = await bot.call_foo_bar(
            bot_id,
            baz=1,
            callback_timeout=0,
            wait_callback=False,
        )

        # Sleep called twice, 'cause we should take time for alarm to call a callback
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        with pytest.raises(BotXMethodCallbackNotFoundError) as exc:
            await bot.wait_botx_method_callback(foo_bar)

    # - Assert -
    assert "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3" in str(exc.value)
    assert "timed out" in str(exc.value)
    assert endpoint.called
