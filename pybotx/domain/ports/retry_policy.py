from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class RetryPolicyPort(Protocol):
    async def execute(self, func: Callable[[], Awaitable[T]]) -> T: ...  # pragma: no cover
