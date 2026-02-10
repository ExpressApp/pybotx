from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any, TYPE_CHECKING
import asyncio

from pybotx.domain.ports.http_client import (
    HttpClientPort,
    HttpRequest,
    HttpResponse,
    HttpStatusError,
    HttpTimeoutError,
    HttpTransportError,
)

if TYPE_CHECKING:
    import aiohttp


def _load_aiohttp():
    try:
        import aiohttp  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "aiohttp is required for AioHttpClientAdapter. "
            "Install it via `pip install aiohttp` or add it to your dependencies."
        ) from exc
    return aiohttp


class AioHttpResponse(HttpResponse):
    def __init__(
        self,
        *,
        response: "aiohttp.ClientResponse",
        request: HttpRequest,
        body: bytes | None = None,
    ) -> None:
        self._response = response
        self._request = request
        self._body = body

    @property
    def status_code(self) -> int:
        return self._response.status

    @property
    def content(self) -> bytes:
        return self._body or b""

    @property
    def request(self) -> HttpRequest:
        return self._request

    @property
    def headers(self) -> Mapping[str, str]:
        return dict(self._response.headers)

    @property
    def is_closed(self) -> bool:
        return self._response.closed

    async def read(self) -> bytes:
        if self._body is None:
            self._body = await self._response.read()
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code < 400:
            return
        raise HttpStatusError(self)

    def json(self) -> Any:
        return json.loads(self.content)

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        if self._response.closed:
            if self._body:
                yield self._body
            return

        async for chunk in self._response.content.iter_chunked(8192):
            if chunk:
                yield chunk


class AioHttpClientAdapter(HttpClientPort):
    def __init__(
        self,
        *,
        timeout: float,
        session: "aiohttp.ClientSession | None" = None,
    ) -> None:
        aiohttp = _load_aiohttp()
        self._aiohttp = aiohttp
        self._owns_session = session is None
        if session is None:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
        self._session = session

    def _build_request_kwargs(self, request: HttpRequest) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        if request.headers:
            kwargs["headers"] = dict(request.headers)
        if request.params:
            kwargs["params"] = request.params
        if request.json is not None:
            kwargs["json"] = request.json
        if request.data is not None:
            kwargs["data"] = request.data
        if request.timeout is not None:
            kwargs["timeout"] = self._aiohttp.ClientTimeout(total=request.timeout)

        files = request.files
        if not files:
            return kwargs

        form = self._aiohttp.FormData()
        if request.data is not None:
            for key, value in dict(request.data).items():
                form.add_field(key, value)

        for name, value in files.items():
            if isinstance(value, tuple):
                if len(value) == 2:
                    filename, fileobj = value
                    form.add_field(name, fileobj, filename=filename)
                    continue
                if len(value) == 3:
                    filename, fileobj, content_type = value
                    form.add_field(
                        name,
                        fileobj,
                        filename=filename,
                        content_type=content_type,
                    )
                    continue
            form.add_field(name, value)

        kwargs["data"] = form
        return kwargs

    async def send(self, request: HttpRequest) -> HttpResponse:
        kwargs = self._build_request_kwargs(request)
        try:
            async with self._session.request(
                request.method,
                request.url,
                **kwargs,
            ) as response:
                body = await response.read()
                return AioHttpResponse(
                    response=response,
                    request=request,
                    body=body,
                )
        except asyncio.TimeoutError as exc:
            raise HttpTimeoutError(str(exc)) from exc
        except self._aiohttp.ClientError as exc:
            raise HttpTransportError(str(exc)) from exc

    @asynccontextmanager
    async def stream(
        self,
        request: HttpRequest,
    ) -> AsyncIterator[HttpResponse]:
        kwargs = self._build_request_kwargs(request)
        try:
            async with self._session.request(
                request.method,
                request.url,
                **kwargs,
            ) as response:
                yield AioHttpResponse(
                    response=response,
                    request=request,
                )
        except asyncio.TimeoutError as exc:
            raise HttpTimeoutError(str(exc)) from exc
        except self._aiohttp.ClientError as exc:
            raise HttpTransportError(str(exc)) from exc

    async def aclose(self) -> None:
        if self._owns_session:
            await self._session.close()
