from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable
from collections.abc import AsyncIterator, Mapping
from contextlib import AbstractAsyncContextManager


@dataclass(slots=True)
class HttpRequest:
    method: str
    url: str
    headers: Mapping[str, str] | None = None
    params: Mapping[str, Any] | None = None
    json: Any | None = None
    data: Any | None = None
    files: Mapping[str, Any] | None = None
    timeout: float | None = None


class HttpClientError(Exception):
    """Base HTTP client error."""


class HttpTransportError(HttpClientError):
    """Network/transport-level error."""


class HttpTimeoutError(HttpTransportError):
    """HTTP request timed out."""


class HttpStatusError(HttpClientError):
    def __init__(self, response: "HttpResponse") -> None:
        self.response = response
        super().__init__(f"HTTP status {response.status_code}")


@runtime_checkable
class HttpResponse(Protocol):
    status_code: int
    headers: Mapping[str, str]
    content: bytes
    request: HttpRequest
    is_closed: bool

    async def read(self) -> bytes: ...  # pragma: no cover

    def json(self) -> Any: ...  # pragma: no cover

    async def iter_bytes(self) -> AsyncIterator[bytes]: ...  # pragma: no cover

    def raise_for_status(self) -> None: ...  # pragma: no cover


@runtime_checkable
class HttpClientPort(Protocol):
    async def send(self, request: HttpRequest) -> HttpResponse: ...  # pragma: no cover

    def stream(
        self,
        request: HttpRequest,
    ) -> AbstractAsyncContextManager[HttpResponse]: ...  # pragma: no cover

    async def aclose(self) -> None: ...  # pragma: no cover


__all__ = (
    "HttpClientError",
    "HttpClientPort",
    "HttpRequest",
    "HttpResponse",
    "HttpStatusError",
    "HttpTimeoutError",
    "HttpTransportError",
)
