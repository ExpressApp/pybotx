import asyncio
import pytest
from uuid import uuid4

from pybotx.bot.callbacks.callback_manager import (
    CallbackManager,
    CallbackAlarm,
    _callback_timeout_alarm,
)
from pybotx.bot.exceptions import BotXMethodCallbackNotFoundError


@pytest.mark.asyncio
async def test_delegation_to_repo_methods(monkeypatch):
    """Проверяем, что CallbackManager делегирует все вызовы в CallbackRepoProto."""
    sync_id = uuid4()
    calls = []

    class DummyRepo:
        async def create_botx_method_callback(self, sid):
            calls.append(("create", sid))

        async def set_botx_method_callback_result(self, cb):
            calls.append(("set", cb))

        async def wait_botx_method_callback(self, sid, timeout):
            calls.append(("wait", sid, timeout))
            return "result"

        async def pop_botx_method_callback(self, sid):
            calls.append(("pop", sid))
            return "future"

        async def stop_callbacks_waiting(self):
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
    assert res == "result"
    # pop
    fut = await mgr.pop_botx_method_callback(sync_id)
    assert fut == "future"
    # stop
    await mgr.stop_callbacks_waiting()

    assert calls == [
        ("create", sync_id),
        ("set", dummy_cb),
        ("wait", sync_id, 2.5),
        ("pop", sync_id),
        ("stop",),
    ]


def test_get_event_loop_prefers_main_loop():
    """Если задан основной луп, _get_event_loop возвращает именно его."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    loop = asyncio.new_event_loop()
    mgr.set_main_loop(loop)
    assert mgr._get_event_loop() is loop


def test_get_event_loop_fallback_to_current():
    """Если основной луп не задан, _get_event_loop возвращает текущий луп."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    # main_loop не задан (None по умолчанию)
    assert mgr._main_loop is None
    # должен вернуть текущий луп
    current_loop = asyncio.get_event_loop()
    assert mgr._get_event_loop() is current_loop


@pytest.mark.asyncio
async def test_setup_and_cancel_alarm_default_and_with_return():
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


def test_cancel_nonexistent_raises():
    """Если нет такого таймера, должно быть BotXMethodCallbackNotFoundError."""
    repo = type("R", (), {})()
    mgr = CallbackManager(repo)
    with pytest.raises(BotXMethodCallbackNotFoundError):
        mgr.cancel_callback_timeout_alarm(uuid4())


@pytest.mark.asyncio
async def test_callback_timeout_alarm_triggers(monkeypatch):
    """
    Проверяем логику _callback_timeout_alarm:
      - после await sleep вызывает cancel_callback_timeout_alarm и pop_botx_method_callback;
      - логирует ошибку.
    """
    sid = uuid4()
    calls = []

    class DummyMgr(CallbackManager):
        def __init__(self):
            super().__init__(None)

        def cancel_callback_timeout_alarm(self, sync_id):
            calls.append(("cancel", sync_id))

        async def pop_botx_method_callback(self, sync_id):
            calls.append(("pop", sync_id))

    mgr = DummyMgr()

    # Подменяем sleep, чтобы не ждать реальное время
    async def fake_sleep(t):
        calls.append(("sleep", t))
        # не ждём

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Подменяем logger.error
    logged = {}
    from pybotx.logger import logger

    def fake_error(msg, **kwargs):
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
