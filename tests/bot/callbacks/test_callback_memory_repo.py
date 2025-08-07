import asyncio
import threading
import time
from typing import Any
from uuid import UUID, uuid4

import pytest

from pybotx.bot.callbacks.callback_memory_repo import (
    CallbackWrapper,
    CallbackMemoryRepo,
)
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.models.method_callbacks import (
    BotAPIMethodSuccessfulCallback,
    BotAPIMethodFailedCallback,
)


def create_successful_callback(sync_id: UUID) -> BotAPIMethodSuccessfulCallback:
    """Create a mock successful callback for testing."""
    return BotAPIMethodSuccessfulCallback(
        sync_id=sync_id, status="ok", result={"test": "data"}
    )


def create_failed_callback(sync_id: UUID) -> BotAPIMethodFailedCallback:
    """Create a mock failed callback for testing."""
    return BotAPIMethodFailedCallback(
        sync_id=sync_id,
        status="error",
        reason="test error",
        errors=["test error"],
        error_data={"test": "error_data"},
    )


@pytest.mark.asyncio
async def test_create_future_without_main_loop_and_set_result_and_wait() -> None:
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)
    wrapper.create_future()
    assert wrapper._future is not None

    result = create_successful_callback(sync_id)
    wrapper.set_result(result)

    got = await wrapper.wait_for_result(timeout=1)
    assert got is result
    # asyncio.Future хранит результат
    assert wrapper._future.result() is result
    assert wrapper._result is result


@pytest.mark.asyncio
async def test_set_exception_and_wait_for_exception_wrapper() -> None:
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)
    wrapper.create_future()

    exc = RuntimeError("test error")
    wrapper.set_exception(exc)

    with pytest.raises(RuntimeError) as ei:
        await wrapper.wait_for_result(timeout=1)
    assert ei.value is exc

    with pytest.raises(RuntimeError):
        wrapper._future.result()  # type: ignore
    assert wrapper._exception is exc


def test_get_future_before_create_raises_wrapper() -> None:
    wrapper = CallbackWrapper(uuid4())
    with pytest.raises(RuntimeError):
        wrapper.get_future()


@pytest.mark.asyncio
async def test_create_future_with_main_loop_equal_and_set_result_wrapper() -> None:
    sync_id = uuid4()
    loop = asyncio.get_running_loop()
    wrapper = CallbackWrapper(sync_id, main_loop=loop)
    wrapper.create_future()
    assert wrapper._future is not None

    dummy = create_successful_callback(sync_id)
    wrapper.set_result(dummy)
    assert wrapper._future.result() == dummy

    got = await wrapper.wait_for_result(timeout=1)
    assert got == dummy


def test_create_future_with_different_main_loop_wrapper() -> None:
    sync_id = uuid4()
    other_loop = asyncio.new_event_loop()

    def loop_runner() -> None:
        asyncio.set_event_loop(other_loop)
        other_loop.run_forever()

    thread = threading.Thread(target=loop_runner, daemon=True)
    thread.start()

    try:
        wrapper = CallbackWrapper(sync_id, main_loop=other_loop)
        wrapper.create_future()

        deadline = time.time() + 1.0
        while wrapper._future is None and time.time() < deadline:
            time.sleep(0.01)

        assert wrapper._future is not None
        # Future привязана к other_loop
        assert wrapper._future.get_loop() == other_loop
    finally:
        other_loop.call_soon_threadsafe(other_loop.stop)
        thread.join(timeout=1)


def test_create_future_branch_main_loop_not_equal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sync_id = uuid4()
    called = {}

    class FakeLoop:
        def call_soon_threadsafe(self, fn: Any, *args: Any) -> None:
            called["ok"] = True
            fn(*args)

    fake_loop = FakeLoop()
    # Симулируем, что get_running_loop() вернёт «чужой» луп
    monkeypatch.setattr(asyncio, "get_running_loop", lambda: object())

    wrapper = CallbackWrapper(sync_id, main_loop=fake_loop)  # type: ignore
    wrapper.create_future()

    assert called.get("ok", False)
    # После этого future должен быть создан
    fut = wrapper.get_future()
    assert isinstance(fut, asyncio.Future)


def test_create_future_exception_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    sync_id = uuid4()
    called = {}

    class FakeLoop:
        def call_soon_threadsafe(self, fn: Any, *args: Any) -> None:
            called["ok"] = True
            fn(*args)

    fake_loop = FakeLoop()

    # Симулируем RuntimeError внутри get_running_loop()
    def bad_loop() -> None:
        raise RuntimeError

    monkeypatch.setattr(asyncio, "get_running_loop", bad_loop)

    wrapper = CallbackWrapper(sync_id, main_loop=fake_loop)  # type: ignore
    wrapper.create_future()

    assert called.get("ok", False)
    fut = wrapper.get_future()
    assert isinstance(fut, asyncio.Future)


@pytest.mark.asyncio
async def test_set_exception_with_main_loop_equal_wrapper() -> None:
    sync_id = uuid4()
    loop = asyncio.get_running_loop()
    wrapper = CallbackWrapper(sync_id, main_loop=loop)
    wrapper.create_future()

    exc = ValueError("val")
    wrapper.set_exception(exc)

    with pytest.raises(ValueError):
        wrapper._future.result()  # type: ignore

    with pytest.raises(ValueError):
        await wrapper.wait_for_result(timeout=1)


@pytest.mark.asyncio
async def test_wait_for_result_runtime_error_branch_success_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)
    wrapper.create_future()
    result = create_successful_callback(sync_id)
    wrapper.set_result(result)

    # Теперь внутри wait_for_result get_running_loop бросит RuntimeError
    monkeypatch.setattr(
        asyncio, "get_running_loop", lambda: (_ for _ in ()).throw(RuntimeError())
    )

    got = await wrapper.wait_for_result(timeout=1)
    assert got == result


@pytest.mark.asyncio
async def test_wait_for_result_runtime_error_branch_exception_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)
    wrapper.create_future()

    exc = AttributeError("a")
    wrapper.set_exception(exc)

    monkeypatch.setattr(
        asyncio, "get_running_loop", lambda: (_ for _ in ()).throw(RuntimeError())
    )

    with pytest.raises(AttributeError):
        await wrapper.wait_for_result(timeout=1)


@pytest.mark.asyncio
async def test_wait_for_result_runtime_error_branch_timeout_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)
    wrapper.create_future()

    monkeypatch.setattr(
        asyncio, "get_running_loop", lambda: (_ for _ in ()).throw(RuntimeError())
    )

    with pytest.raises(asyncio.TimeoutError):
        await wrapper.wait_for_result(timeout=0.01)


@pytest.mark.asyncio
async def test_memory_repo_full_cycle() -> None:
    repo = CallbackMemoryRepo()
    sync_id = uuid4()

    # create → set → wait
    await repo.create_botx_method_callback(sync_id)

    cb = create_successful_callback(sync_id)
    await repo.set_botx_method_callback_result(cb)
    got = await repo.wait_botx_method_callback(sync_id, timeout=1)
    assert got is cb

    # pop (сначала создаём снова, т.к. wait удалил обёртку)
    await repo.create_botx_method_callback(sync_id)
    w = repo._callback_wrappers[sync_id]
    w.set_result(cb)
    fut = await repo.pop_botx_method_callback(sync_id)
    assert isinstance(fut, asyncio.Future)
    assert fut.result() is cb


@pytest.mark.asyncio
async def test_wait_timeout_removes_and_raises_callback_not_received() -> None:
    repo = CallbackMemoryRepo()
    sync_id = uuid4()
    await repo.create_botx_method_callback(sync_id)

    with pytest.raises(CallbackNotReceivedError):
        await repo.wait_botx_method_callback(sync_id, timeout=0.01)

    assert sync_id not in repo._callback_wrappers


@pytest.mark.asyncio
async def test_set_without_create_raises_not_found_repo() -> None:
    repo = CallbackMemoryRepo()

    dummy_callback = create_successful_callback(uuid4())
    with pytest.raises(BotXMethodCallbackNotFoundError):
        await repo.set_botx_method_callback_result(dummy_callback)


@pytest.mark.asyncio
async def test_wait_without_create_raises_not_found_repo() -> None:
    repo = CallbackMemoryRepo()
    with pytest.raises(BotXMethodCallbackNotFoundError):
        await repo.wait_botx_method_callback(uuid4(), timeout=0.1)


@pytest.mark.asyncio
async def test_pop_without_create_raises_keyerror_repo() -> None:
    repo = CallbackMemoryRepo()
    with pytest.raises(KeyError):
        await repo.pop_botx_method_callback(uuid4())


@pytest.mark.asyncio
async def test_stop_callbacks_waiting_sets_exceptions_repo() -> None:
    repo = CallbackMemoryRepo()
    sync_ids = [uuid4() for _ in range(3)]
    for sid in sync_ids:
        await repo.create_botx_method_callback(sid)

    await repo.stop_callbacks_waiting()

    for sid in sync_ids:
        w = repo._callback_wrappers[sid]
        assert w._event.is_set()
        assert isinstance(w._exception, BotShuttingDownError)
        with pytest.raises(BotShuttingDownError):
            w.get_future().result()


@pytest.mark.asyncio
async def test_get_event_loop_default_and_set_main_loop_repo() -> None:
    repo = CallbackMemoryRepo()

    # по-умолчанию — текущий loop
    assert repo._get_event_loop() is asyncio.get_event_loop()

    # после установки — возвращается заданный
    new_loop = asyncio.new_event_loop()
    repo.set_main_loop(new_loop)
    assert repo._get_event_loop() is new_loop


class DummyLoop:
    """Простейший loop-stub с немедленным выполнением call_soon_threadsafe."""

    def __init__(self) -> None:
        self.scheduled: list[tuple[Any, tuple[Any, ...]]] = []

    def call_soon_threadsafe(self, fn: Any, *args: Any) -> None:
        self.scheduled.append((fn, args))
        fn(*args)


@pytest.mark.asyncio
async def test_set_result_main_loop_not_equal() -> None:
    """Ветка set_result: main_loop задан и ≠ текущего, должно зайти в call_soon_threadsafe + run_in_executor."""
    sync_id = uuid4()
    fake_loop = DummyLoop()
    wrapper = CallbackWrapper(sync_id, main_loop=fake_loop)  # type: ignore
    wrapper.create_future()

    # set_result должен через fake_loop вызвать fut.set_result
    result = create_successful_callback(sync_id)
    wrapper.set_result(result)
    assert fake_loop.scheduled, "ожидали call_soon_threadsafe"
    # событие и _result в любом случае
    assert wrapper._event.is_set() and wrapper._result == result

    # wait_for_result через настоящий loop.run_in_executor вернёт результат
    got = await wrapper.wait_for_result(timeout=0.1)
    assert got == result


@pytest.mark.asyncio
async def test_set_exception_main_loop_not_equal() -> None:
    """Ветка set_exception: main_loop задан и ≠ текущего → call_soon_threadsafe + поднятие исключения."""
    sync_id = uuid4()
    fake_loop = DummyLoop()
    wrapper = CallbackWrapper(sync_id, main_loop=fake_loop)  # type: ignore
    wrapper.create_future()

    err = ValueError("boom")
    wrapper.set_exception(err)

    assert fake_loop.scheduled, "ожидали call_soon_threadsafe для set_exception"
    with pytest.raises(ValueError) as exc:
        await wrapper.wait_for_result(timeout=0.1)
    assert str(exc.value) == "boom"


@pytest.mark.asyncio
async def test_create_future_main_loop_none_after_runtime_error() -> None:
    """Тест для покрытия линии 43: когда main_loop становится None после RuntimeError."""
    sync_id = uuid4()

    # Создаём wrapper с main_loop
    main_loop = asyncio.new_event_loop()
    wrapper = CallbackWrapper(sync_id, main_loop=main_loop)

    # Мокаем get_running_loop чтобы он выбросил RuntimeError
    original_get_running_loop = asyncio.get_running_loop
    call_count = 0

    def mock_get_running_loop() -> None:
        nonlocal call_count
        call_count += 1
        # При первом вызове устанавливаем main_loop в None
        if call_count == 1:
            wrapper.main_loop = None
        raise RuntimeError("No running event loop")

    # Подменяем get_running_loop
    asyncio.get_running_loop = mock_get_running_loop  # type: ignore

    try:
        wrapper.create_future()
        # Проверяем что future создался
        assert wrapper._future is not None
        # Проверяем что main_loop стал None
        assert wrapper.main_loop is None
    finally:
        # Восстанавливаем оригинальную функцию
        asyncio.get_running_loop = original_get_running_loop


def test_set_result_runtime_error_handling() -> None:
    """Тест для покрытия линий 60-61: обработка RuntimeError в set_result."""
    sync_id = uuid4()
    main_loop = asyncio.new_event_loop()
    wrapper = CallbackWrapper(sync_id, main_loop=main_loop)

    # Создаём future напрямую, чтобы обойти логику create_future
    wrapper._future = asyncio.Future()

    # Мокаем get_running_loop чтобы он выбросил RuntimeError
    original_get_running_loop = asyncio.get_running_loop

    def mock_get_running_loop() -> None:
        raise RuntimeError("No running event loop")

    # Мокаем call_soon_threadsafe чтобы отследить вызов
    calls: list[tuple[Any, tuple[Any, ...]]] = []

    def mock_call_soon_threadsafe(fn: Any, *args: Any) -> None:
        calls.append((fn, args))
        # Не вызываем fn(*args) чтобы избежать ошибок с future

    main_loop.call_soon_threadsafe = mock_call_soon_threadsafe  # type: ignore
    asyncio.get_running_loop = mock_get_running_loop  # type: ignore

    try:
        result = create_successful_callback(sync_id)
        wrapper.set_result(result)
        # Проверяем что call_soon_threadsafe был вызван
        assert len(calls) == 1
        assert wrapper._result == result
        # Проверяем что вызвали правильную функцию
        fn, args = calls[0]
        assert fn == wrapper._future.set_result
        assert args == (result,)
    finally:
        asyncio.get_running_loop = original_get_running_loop


def test_set_exception_runtime_error_handling() -> None:
    """Тест для покрытия линий 79-80: обработка RuntimeError в set_exception."""
    sync_id = uuid4()
    main_loop = asyncio.new_event_loop()
    wrapper = CallbackWrapper(sync_id, main_loop=main_loop)

    # Создаём future напрямую, чтобы обойти логику create_future
    wrapper._future = asyncio.Future()

    # Мокаем get_running_loop чтобы он выбросил RuntimeError
    original_get_running_loop = asyncio.get_running_loop

    def mock_get_running_loop() -> None:
        raise RuntimeError("No running event loop")

    # Мокаем call_soon_threadsafe чтобы отследить вызов
    calls: list[tuple[Any, tuple[Any, ...]]] = []

    def mock_call_soon_threadsafe(fn: Any, *args: Any) -> None:
        calls.append((fn, args))
        # Не вызываем fn(*args) чтобы избежать ошибок с future

    main_loop.call_soon_threadsafe = mock_call_soon_threadsafe  # type: ignore
    asyncio.get_running_loop = mock_get_running_loop  # type: ignore

    test_exception = ValueError("test error")

    try:
        wrapper.set_exception(test_exception)
        # Проверяем что call_soon_threadsafe был вызван
        assert len(calls) == 1
        assert wrapper._exception is test_exception
        # Проверяем что вызвали правильную функцию
        fn, args = calls[0]
        assert fn == wrapper._future.set_exception
        assert args == (test_exception,)
    finally:
        asyncio.get_running_loop = original_get_running_loop


def test_set_result_future_none_branch() -> None:
    """Тест для покрытия ветки 52->exit: когда _future is None."""
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)

    # Не создаём future, оставляем None
    assert wrapper._future is None

    # Вызываем set_result - должен установить результат, но не работать с future
    result = create_successful_callback(sync_id)
    wrapper.set_result(result)
    assert wrapper._result == result
    assert wrapper._event.is_set()


def test_set_result_future_done_branch() -> None:
    """Тест для покрытия ветки 52->exit: когда _future.done() is True."""
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)

    # Создаём future и завершаем его
    wrapper._future = asyncio.Future()
    already_done_result = create_successful_callback(sync_id)
    wrapper._future.set_result(already_done_result)
    assert wrapper._future.done()

    # Вызываем set_result - должен установить результат, но не работать с future
    new_result = create_failed_callback(sync_id)
    wrapper.set_result(new_result)
    assert wrapper._result == new_result
    assert wrapper._event.is_set()
    # Future должен остаться с прежним результатом
    assert wrapper._future.result() == already_done_result


def test_set_exception_future_none_branch() -> None:
    """Тест для покрытия ветки 71->exit: когда _future is None."""
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)

    # Не создаём future, оставляем None
    assert wrapper._future is None

    test_exception = ValueError("test error")

    # Вызываем set_exception - должен установить исключение, но не работать с future
    wrapper.set_exception(test_exception)
    assert wrapper._exception is test_exception
    assert wrapper._event.is_set()


def test_set_exception_future_done_branch() -> None:
    """Тест для покрытия ветки 71->exit: когда _future.done() is True."""
    sync_id = uuid4()
    wrapper = CallbackWrapper(sync_id)

    # Создаём future и завершаем его
    wrapper._future = asyncio.Future()
    already_done_result = create_successful_callback(sync_id)
    wrapper._future.set_result(already_done_result)
    assert wrapper._future.done()

    test_exception = ValueError("test error")

    # Вызываем set_exception - должен установить исключение, но не работать с future
    wrapper.set_exception(test_exception)
    assert wrapper._exception is test_exception
    assert wrapper._event.is_set()
    # Future должен остаться с прежним результатом
    assert wrapper._future.result() == already_done_result
