from dataclasses import dataclass, field
from typing import Protocol
from collections.abc import Callable

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from pybotx.constants import (
    BOTX_HTTP_CONNECT_TIMEOUT_SECONDS,
    BOTX_HTTP_KEEPALIVE_EXPIRY_SECONDS,
    BOTX_HTTP_MAX_CONNECTIONS,
    BOTX_HTTP_MAX_KEEPALIVE_CONNECTIONS,
    BOTX_HTTP_POOL_TIMEOUT_SECONDS,
    BOTX_HTTP_READ_TIMEOUT_SECONDS,
    BOTX_HTTP_RETRY_ATTEMPTS,
    BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS,
    BOTX_HTTP_RETRY_JITTER_SECONDS,
    BOTX_HTTP_RETRY_MAX_DELAY_SECONDS,
    BOTX_HTTP_WRITE_TIMEOUT_SECONDS,
)

DEFAULT_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
RetryExceptionTypes = tuple[type[BaseException], ...]
BeforeSleepHandler = Callable[[RetryCallState], None]


def build_default_httpx_timeout() -> httpx.Timeout:
    return httpx.Timeout(
        connect=BOTX_HTTP_CONNECT_TIMEOUT_SECONDS,
        read=BOTX_HTTP_READ_TIMEOUT_SECONDS,
        write=BOTX_HTTP_WRITE_TIMEOUT_SECONDS,
        pool=BOTX_HTTP_POOL_TIMEOUT_SECONDS,
    )


def build_default_httpx_limits() -> httpx.Limits:
    return httpx.Limits(
        max_connections=BOTX_HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=BOTX_HTTP_MAX_KEEPALIVE_CONNECTIONS,
        keepalive_expiry=BOTX_HTTP_KEEPALIVE_EXPIRY_SECONDS,
    )


@dataclass(frozen=True, slots=True)
class BotXRetryPolicy:
    max_attempts: int = BOTX_HTTP_RETRY_ATTEMPTS
    initial_delay_seconds: float = BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS
    max_delay_seconds: float = BOTX_HTTP_RETRY_MAX_DELAY_SECONDS
    jitter_seconds: float = BOTX_HTTP_RETRY_JITTER_SECONDS
    retryable_status_codes: frozenset[int] = field(
        default_factory=lambda: DEFAULT_RETRYABLE_STATUS_CODES,
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("Retry max attempts should be greater than 0")
        if self.initial_delay_seconds < 0:
            raise ValueError("Retry initial delay should be greater or equal to 0")
        if self.max_delay_seconds < 0:
            raise ValueError("Retry max delay should be greater or equal to 0")
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError(
                "Retry max delay should be greater or equal to initial delay",
            )
        if self.jitter_seconds < 0:
            raise ValueError("Retry jitter should be greater or equal to 0")


class BotXRetryStrategy(Protocol):
    def build_retrying(
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: RetryExceptionTypes,
        before_sleep: BeforeSleepHandler,
    ) -> AsyncRetrying: ...


@dataclass(frozen=True, slots=True)
class TenacityRetryStrategy(BotXRetryStrategy):
    def build_retrying(
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: RetryExceptionTypes,
        before_sleep: BeforeSleepHandler,
    ) -> AsyncRetrying:
        return AsyncRetrying(
            stop=stop_after_attempt(retry_policy.max_attempts),
            wait=wait_exponential_jitter(
                initial=retry_policy.initial_delay_seconds,
                max=retry_policy.max_delay_seconds,
                jitter=retry_policy.jitter_seconds,
            ),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep,
            reraise=True,
        )
