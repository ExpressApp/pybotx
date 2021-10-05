import asyncio
from http import HTTPStatus
from typing import NoReturn, Optional
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, lifespan_wrapper
from botx.bot.models.botx_method_callbacks import BotXMethodCallbackFailed
from botx.client.botx_method import BotXMethod, ErrorCallbackHandlers
from botx.client.exceptions.callbacks import (
    BotXMethodCallbackFailedReceived,
    CallbackNotReceivedError,
)
from tests.client.test_botx_method import (
    BotXAPIFooBarRequestPayload,
    BotXAPIFooBarResponsePayload,
)


def error_callback_handler(callback: BotXMethodCallbackFailed) -> NoReturn:
    raise BotXMethodCallbackFailedReceived(callback)


class FooBarCallbackMethod(BotXMethod):
    error_callback_handlers: ErrorCallbackHandlers = {
        "foo_bar_error": error_callback_handler,
    }

    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[int],
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        api_model = self._extract_api_model(BotXAPIFooBarResponsePayload, response)

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
        )

        return api_model


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

    method = FooBarCallbackMethod(
        bot_id,
        built_bot._httpx_client,  # noqa: WPS437 (Attaching method to bot in runtime)
        built_bot._bot_accounts_storage,  # noqa: WPS437
        built_bot._botx_methods_callbacks_manager,  # noqa: WPS437
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            method.execute(payload, wait_callback=True, callback_timeout=None),
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

        with pytest.raises(BotXMethodCallbackFailedReceived) as exc:
            await task

    # - Assert -
    assert "foo_bar_error" in str(exc.value)
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

    method = FooBarCallbackMethod(
        bot_id,
        built_bot._httpx_client,  # noqa: WPS437 (Attaching method to bot in runtime)
        built_bot._bot_accounts_storage,  # noqa: WPS437
        built_bot._botx_methods_callbacks_manager,  # noqa: WPS437
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            method.execute(payload, wait_callback=True, callback_timeout=None),
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

        with pytest.raises(BotXMethodCallbackFailedReceived) as exc:
            await task

    # - Assert -
    assert "failed with" in str(exc.value)
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

    method = FooBarCallbackMethod(
        bot_id,
        built_bot._httpx_client,  # noqa: WPS437 (Attaching method to bot in runtime)
        built_bot._bot_accounts_storage,  # noqa: WPS437
        built_bot._botx_methods_callbacks_manager,  # noqa: WPS437
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallbackNotReceivedError) as exc:
            await method.execute(payload, wait_callback=True, callback_timeout=0)

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

    method = FooBarCallbackMethod(
        bot_id,
        built_bot._httpx_client,  # noqa: WPS437 (Attaching method to bot in runtime)
        built_bot._bot_accounts_storage,  # noqa: WPS437
        built_bot._botx_methods_callbacks_manager,  # noqa: WPS437
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    async with lifespan_wrapper(built_bot):
        botx_api_foo_bar = await method.execute(
            payload,
            wait_callback=False,
            callback_timeout=None,
        )

    # - Assert -
    assert botx_api_foo_bar.to_domain() == sync_id
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

    method = FooBarCallbackMethod(
        bot_id,
        built_bot._httpx_client,  # noqa: WPS437 (Attaching method to bot in runtime)
        built_bot._bot_accounts_storage,  # noqa: WPS437
        built_bot._botx_methods_callbacks_manager,  # noqa: WPS437
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            method.execute(payload, wait_callback=True, callback_timeout=None),
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
    assert (await task).to_domain() == sync_id
    assert endpoint.called
