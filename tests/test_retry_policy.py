import sys
import types

import pytest

from pybotx.infrastructure.retry_policy import NoopRetryPolicy, TenacityRetryPolicy


class _Attempt:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def _install_tenacity_stub(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("tenacity")
    module.retry_calls = []
    module.wait_jitter_calls = []
    module.wait_calls = []
    module.stop_calls = []
    module.retrying_kwargs = None

    def retry_if_exception_type(exc_types):
        module.retry_calls.append(exc_types)
        return ("retry", exc_types)

    def wait_exponential_jitter(*, initial: float, max: float, exp_base: float):
        payload = {"initial": initial, "max": max, "exp_base": exp_base}
        module.wait_jitter_calls.append(payload)
        return ("wait_jitter", payload)

    def wait_exponential(*, multiplier: float, max: float, exp_base: float):
        payload = {"multiplier": multiplier, "max": max, "exp_base": exp_base}
        module.wait_calls.append(payload)
        return ("wait", payload)

    def stop_after_attempt(attempts: int):
        module.stop_calls.append(attempts)
        return ("stop", attempts)

    class AsyncRetrying:
        def __init__(self, **kwargs):
            module.retrying_kwargs = kwargs
            self._done = False

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self._done:
                raise StopAsyncIteration
            self._done = True
            return _Attempt()

    module.retry_if_exception_type = retry_if_exception_type
    module.wait_exponential_jitter = wait_exponential_jitter
    module.wait_exponential = wait_exponential
    module.stop_after_attempt = stop_after_attempt
    module.AsyncRetrying = AsyncRetrying

    monkeypatch.setitem(sys.modules, "tenacity", module)
    return module


@pytest.mark.asyncio
async def test__noop_retry_policy__executes() -> None:
    policy = NoopRetryPolicy()

    async def _work():
        return "ok"

    assert await policy.execute(_work) == "ok"


@pytest.mark.asyncio
async def test__tenacity_retry_policy__disabled_skips_retrying(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenacity_stub = _install_tenacity_stub(monkeypatch)
    wait_override = object()
    retry_override = object()
    stop_override = object()

    policy = TenacityRetryPolicy(
        enabled=False,
        wait=wait_override,
        retry=retry_override,
        stop=stop_override,
    )

    async def _work():
        return "ok"

    result = await policy.execute(_work)

    assert result == "ok"
    assert policy._wait is wait_override
    assert policy._retry is retry_override
    assert policy._stop is stop_override
    assert tenacity_stub.retrying_kwargs is None


@pytest.mark.asyncio
async def test__tenacity_retry_policy__enabled_with_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenacity_stub = _install_tenacity_stub(monkeypatch)

    policy = TenacityRetryPolicy(
        enabled=True,
        jitter=True,
        min_delay=0.5,
        max_delay=3.0,
        multiplier=4.0,
        max_attempts=5,
        retry_on_exceptions=(ValueError,),
    )

    async def _work():
        return "ok"

    result = await policy.execute(_work)

    assert result == "ok"
    assert tenacity_stub.wait_jitter_calls == [
        {"initial": 0.5, "max": 3.0, "exp_base": 4.0}
    ]
    assert tenacity_stub.stop_calls == [5]
    assert tenacity_stub.retry_calls == [(ValueError,)]
    assert tenacity_stub.retrying_kwargs is not None
    assert tenacity_stub.retrying_kwargs["wait"] == policy._wait


@pytest.mark.asyncio
async def test__tenacity_retry_policy__enabled_without_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenacity_stub = _install_tenacity_stub(monkeypatch)

    policy = TenacityRetryPolicy(
        enabled=True,
        jitter=False,
        min_delay=0.2,
        max_delay=5.0,
        multiplier=3.0,
        max_attempts=2,
    )

    async def _work():
        return "ok"

    result = await policy.execute(_work)

    assert result == "ok"
    assert tenacity_stub.wait_calls == [
        {"multiplier": 0.2, "max": 5.0, "exp_base": 3.0}
    ]
    assert tenacity_stub.stop_calls == [2]
    assert tenacity_stub.retrying_kwargs is not None
    assert tenacity_stub.retrying_kwargs["wait"] == policy._wait


@pytest.mark.asyncio
async def test__tenacity_retry_policy__exhausted_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = types.ModuleType("tenacity")

    def retry_if_exception_type(exc_types):  # type: ignore[no-untyped-def]
        return ("retry", exc_types)

    def wait_exponential_jitter(*args, **kwargs):  # type: ignore[no-untyped-def]
        return ("wait", args, kwargs)

    def stop_after_attempt(attempts: int):
        return ("stop", attempts)

    class AsyncRetrying:
        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            self._done = True

        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    module.retry_if_exception_type = retry_if_exception_type
    module.wait_exponential_jitter = wait_exponential_jitter
    module.wait_exponential = wait_exponential_jitter
    module.stop_after_attempt = stop_after_attempt
    module.AsyncRetrying = AsyncRetrying

    monkeypatch.setitem(sys.modules, "tenacity", module)

    policy = TenacityRetryPolicy(enabled=True)

    async def _work():
        return "ok"

    with pytest.raises(RuntimeError):
        await policy.execute(_work)
