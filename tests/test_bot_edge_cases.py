import asyncio
from typing import Any
from uuid import UUID

import pytest

from pybotx import Bot, BotXRetryPolicy, HandlerCollector
from pybotx.bot.bot_accounts_storage import BotAccountsStorage


@pytest.mark.asyncio
async def test__dispatch_raw_command__supports_wait_modes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])
    completed = False

    async def execute() -> None:
        nonlocal completed
        completed = True

    def start(_self: Bot, *_args: Any, **_kwargs: Any) -> asyncio.Task[None]:
        return asyncio.create_task(execute())

    monkeypatch.setattr(Bot, "async_execute_raw_bot_command", start)

    await bot.dispatch_raw_command({}, wait=True)
    assert completed is True

    completed = False
    await bot.dispatch_raw_command({}, wait=False)
    await asyncio.sleep(0)
    assert completed is True
    await bot.shutdown()


@pytest.mark.asyncio
async def test__bot_correlation_extractors_cover_invalid_and_optional_inputs() -> None:
    bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])
    uuid = UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")

    assert bot._extract_trace_id(
        {"traceparent": "00-not-a-valid-trace-id-span-01", "b3": "also-invalid"},
        "fallback",
    ) == "fallback"
    assert bot._extract_bot_id(None) is None
    assert bot._extract_chat_id(None) is None
    assert bot._extract_uuid(uuid) is uuid
    assert bot._extract_uuid("not-a-uuid") is None
    await bot.shutdown()


@pytest.mark.asyncio
async def test__bot_allows_storage_without_resolved_retry_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        BotAccountsStorage,
        "get_retry_request_policy",
        lambda _self: None,
    )
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[],
        retry_policy=BotXRetryPolicy(),
    )
    await bot.shutdown()
