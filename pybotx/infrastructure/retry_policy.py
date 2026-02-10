from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import Any, TypeVar

from pybotx.domain.ports.retry_policy import RetryPolicyPort
from pybotx.domain.ports.http_client import HttpClientError

T = TypeVar("T")


class NoopRetryPolicy(RetryPolicyPort):
    async def execute(self, func: Callable[[], Awaitable[T]]) -> T:
        return await func()


class TenacityRetryPolicy(RetryPolicyPort):
    def __init__(
        self,
        *,
        enabled: bool = True,
        max_attempts: int = 3,
        min_delay: float = 0.1,
        max_delay: float = 2.0,
        multiplier: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: Sequence[type[BaseException]] | None = None,
        retry: Any | None = None,
        wait: Any | None = None,
        stop: Any | None = None,
        before_sleep: Any | None = None,
        reraise: bool = True,
    ) -> None:
        try:
            import tenacity
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "Retry policy requires optional dependency `tenacity`."
            ) from exc

        self._tenacity = tenacity
        self._enabled = enabled
        self._reraise = reraise
        self._before_sleep = before_sleep
        self._retry = retry or tenacity.retry_if_exception_type(
            retry_on_exceptions or (HttpClientError,)
        )
        if wait is not None:
            self._wait = wait
        else:
            if jitter:
                self._wait = tenacity.wait_exponential_jitter(
                    initial=min_delay,
                    max=max_delay,
                    exp_base=multiplier,
                )
            else:
                self._wait = tenacity.wait_exponential(
                    multiplier=min_delay,
                    max=max_delay,
                    exp_base=multiplier,
                )
        self._stop = stop or tenacity.stop_after_attempt(max_attempts)

    async def execute(self, func: Callable[[], Awaitable[T]]) -> T:
        if not self._enabled:
            return await func()

        retrying = self._tenacity.AsyncRetrying(
            retry=self._retry,
            wait=self._wait,
            stop=self._stop,
            before_sleep=self._before_sleep,
            reraise=self._reraise,
        )

        async for attempt in retrying:
            with attempt:
                return await func()

        raise RuntimeError("Retry policy exhausted without result")
