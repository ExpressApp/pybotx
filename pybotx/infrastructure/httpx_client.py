from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

import httpx

from pybotx.domain.ports.http_client import (
    HttpClientPort,
    HttpRequest,
    HttpResponse,
    HttpStatusError,
    HttpTimeoutError,
    HttpTransportError,
)


class HttpxResponse(HttpResponse):
    def __init__(self, *, response: httpx.Response, request: HttpRequest) -> None:
        self._response = response
        self._request = request

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        return dict(self._response.headers)

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def request(self) -> HttpRequest:
        return self._request

    @property
    def is_closed(self) -> bool:
        return self._response.is_closed

    async def read(self) -> bytes:
        if isinstance(self._response.stream, httpx.AsyncByteStream) and not isinstance(
            self._response.stream,
            httpx.SyncByteStream,
        ):
            self._response._content = b"".join(  # type: ignore[attr-defined]
                [chunk async for chunk in self._response.aiter_bytes()]
            )
        else:
            self._response.read()
        return self._response.content

    def json(self) -> Any:
        return self._response.json()

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        async for chunk in self._response.aiter_bytes():
            yield chunk

    def raise_for_status(self) -> None:
        try:
            self._response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HttpStatusError(self) from exc


class HttpxClientAdapter(HttpClientPort):
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def send(self, request: HttpRequest) -> HttpResponse:
        try:
            built_request = self._client.build_request(
                request.method,
                request.url,
                headers=request.headers,
                params=request.params,
                json=request.json,
                data=request.data,
                files=request.files,
                timeout=request.timeout,
            )
            response = await self._client.send(built_request, stream=True)
            if isinstance(response.stream, httpx.AsyncByteStream) and not isinstance(
                response.stream,
                httpx.SyncByteStream,
            ):
                response._content = b"".join(  # type: ignore[attr-defined]
                    [chunk async for chunk in response.aiter_bytes()]
                )
            else:
                response.read()
        except httpx.TimeoutException as exc:
            raise HttpTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise HttpTransportError(str(exc)) from exc
        return HttpxResponse(response=response, request=request)

    @asynccontextmanager
    async def stream(self, request: HttpRequest) -> AsyncIterator[HttpResponse]:
        try:
            async with self._client.stream(
                request.method,
                request.url,
                headers=request.headers,
                params=request.params,
                json=request.json,
                data=request.data,
                files=request.files,
                timeout=request.timeout,
            ) as response:
                yield HttpxResponse(response=response, request=request)
        except httpx.TimeoutException as exc:
            raise HttpTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise HttpTransportError(str(exc)) from exc

    async def aclose(self) -> None:
        await self._client.aclose()


__all__ = ("HttpxClientAdapter",)
