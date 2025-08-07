import asyncio
from typing import Any, List, Union, overload
from uuid import UUID, uuid4

import pytest
from typing_extensions import Literal

from pybotx.models.method_callbacks import BotXMethodCallback

from pybotx.bot.callbacks.callback_manager import (
    CallbackManager,
    CallbackAlarm,
    _callback_timeout_alarm,
)
from pybotx.bot.exceptions import BotXMethodCallbackNotFoundError


@pytest.mark.asyncio
async def test_delegation_to_repo_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверяем, что CallbackManager делегирует все вызовы в CallbackRepoProto."""
    sync_id = uuid4()
    calls: List[Any] = []

    class DummyRepo:
        async def create_botx_method_callback(self, sid: UUID) -> None:
            calls.append(("create", sid))

        async def set_botx_method_callback_result(self, cb: BotXMethodCallback) -> None:
            calls.append(("set", cb))

        async def wait_botx_method_callback(
            self, sid: UUID, timeout: float
        ) -> BotXMethodCallback:
            calls.append(("wait", sid, timeout))
            # Create a mock BotXMethodCallback
            mock_callback = type("MockCallback", (), {"sync_id": sid})()
            return mock_callback  # type: ignore

        async def pop_botx_method_callback(
            self, sid: UUID
        ) -> "asyncio.Future[BotXMethodCallback]":
            calls.append(("pop", sid))
            # Create a mock Future
            future: "asyncio.Future[BotXMethodCallback]" = asyncio.Future()
            future.set_result(type("MockCallback", (), {"sync_id": sid})())
            return future

        async def stop_callbacks_waiting(self) -> None:
            calls.append(("stop",))

    repo = DummyRepo()
    mgr = CallbackManager(repo)
    # create
    await mgr.create_botx_method_callback(sync_id)
    # set result
    dummy_cb = type("C", (), {"sync_id": sync_id})()
    await mgr.set_botx_method_callback_result(dummy_cb)
    # wait
    res = await mgr.wait_botx_method_callback(sync_id, timeout=2.5)
    assert hasattr(res, "sync_id")
    # pop
    fut = await mgr.pop_botx_method_callback(sync_id)
    assert isinstance(fut, asyncio.Future)
    # stop
    await mgr.stop_callbacks_waiting()

    assert calls == [
        ("create", sync_id),
        ("set", dummy_cb),
        ("wait", sync_id, 2.5),
        ("pop", sync_id),
        ("stop",),
    ]


def test_get_event_loop_prefers_main_loop() -> None:
    """Если задан основной луп, _get_event_loop возвращает именно его."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    loop = asyncio.new_event_loop()
    mgr.set_main_loop(loop)
    assert mgr._get_event_loop() is loop


def test_get_event_loop_fallback_to_current() -> None:
    """Если основной луп не задан, _get_event_loop возвращает текущий луп."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    # main_loop не задан (None по умолчанию)
    assert mgr._main_loop is None
    # должен вернуть текущий луп
    current_loop = asyncio.get_event_loop()
    assert mgr._get_event_loop() is current_loop


@pytest.mark.asyncio
async def test_setup_and_cancel_alarm_default_and_with_return() -> None:
    """
    Проверяем, что setup_callback_timeout_alarm создаёт задачу,
    а cancel_callback_timeout_alarm:
      - без return_remaining_time возвращает None;
      - с return_remaining_time=True возвращает оставшееся время в диапазоне [0, timeout];
      - удаляет запись и отменяет таск (task.done() и CancelledError).
    """
    repo = type("R", (), {"create_botx_method_callback": lambda *a, **k: None})()
    mgr = CallbackManager(repo)

    loop = asyncio.get_running_loop()
    mgr.set_main_loop(loop)

    # Часть 1: отмена без возврата времени
    sid1 = uuid4()
    timeout1 = 1.0
    mgr.setup_callback_timeout_alarm(sid1, timeout=timeout1)

    alarm1 = mgr._callback_alarms.get(sid1)
    assert isinstance(alarm1, CallbackAlarm)
    assert not alarm1.task.done()

    result_none = mgr.cancel_callback_timeout_alarm(sid1)
    assert result_none is None
    # Даём событийному циклу обработать отмену
    await asyncio.sleep(0)

    assert sid1 not in mgr._callback_alarms
    assert alarm1.task.done()
    with pytest.raises(asyncio.CancelledError):
        alarm1.task.result()

    # Часть 2: отмена с возвратом оставшегося времени
    sid2 = uuid4()
    timeout2 = 1.5
    mgr.setup_callback_timeout_alarm(sid2, timeout=timeout2)

    alarm2 = mgr._callback_alarms[sid2]
    remaining = mgr.cancel_callback_timeout_alarm(sid2, return_remaining_time=True)

    assert isinstance(remaining, float)
    assert 0.0 <= remaining <= timeout2

    # Даём событийному циклу обработать отмену
    await asyncio.sleep(0)

    assert sid2 not in mgr._callback_alarms
    assert alarm2.task.done()
    with pytest.raises(asyncio.CancelledError):
        alarm2.task.result()


def test_cancel_nonexistent_raises() -> None:
    """Если нет такого таймера, должно быть BotXMethodCallbackNotFoundError."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    with pytest.raises(BotXMethodCallbackNotFoundError):
        mgr.cancel_callback_timeout_alarm(uuid4())


@pytest.mark.asyncio
async def test_callback_timeout_alarm_triggers(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Проверяем логику _callback_timeout_alarm:
      - после await sleep вызывает cancel_callback_timeout_alarm и pop_botx_method_callback;
      - логирует ошибку.
    """
    sid = uuid4()
    calls: List[Any] = []

    class DummyMgr(CallbackManager):
        def __init__(self) -> None:
            super().__init__(None)  # type: ignore

        @overload
        def cancel_callback_timeout_alarm(self, sync_id: UUID) -> None: ...

        @overload
        def cancel_callback_timeout_alarm(
            self, sync_id: UUID, return_remaining_time: Literal[True]
        ) -> float: ...

        def cancel_callback_timeout_alarm(
            self, sync_id: UUID, return_remaining_time: bool = False
        ) -> Union[None, float]:
            calls.append(("cancel", sync_id))
            if return_remaining_time:
                return 0.0
            return None

        async def pop_botx_method_callback(
            self, sync_id: UUID
        ) -> "asyncio.Future[BotXMethodCallback]":
            calls.append(("pop", sync_id))
            future: "asyncio.Future[BotXMethodCallback]" = asyncio.Future()
            future.set_result(type("MockCallback", (), {"sync_id": sync_id})())
            return future

    mgr = DummyMgr()

    # Подменяем sleep, чтобы не ждать реальное время
    async def fake_sleep(t: float) -> None:
        calls.append(("sleep", t))
        # не ждём

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Подменяем logger.error
    logged: dict[str, Any] = {}
    from pybotx.logger import logger

    def fake_error(msg: str, **kwargs: Any) -> None:
        logged["msg"] = msg
        logged["kwargs"] = kwargs

    monkeypatch.setattr(logger, "error", fake_error)

    # Вызываем прямо
    await _callback_timeout_alarm(mgr, sid, timeout=0.5)

    assert ("sleep", 0.5) in calls
    assert ("cancel", sid) in calls
    assert ("pop", sid) in calls
    assert "Callback `{sync_id}` wasn't waited" in logged["msg"]
    assert logged["kwargs"].get("sync_id") == sid
