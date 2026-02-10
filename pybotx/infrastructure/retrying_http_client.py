from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from pybotx.domain.ports.http_client import HttpClientPort, HttpRequest, HttpResponse
from pybotx.domain.ports.retry_policy import RetryPolicyPort


class RetryingHttpClient(HttpClientPort):
    def __init__(
        self,
        *,
        client: HttpClientPort,
        retry_policy: RetryPolicyPort,
        enabled: bool = True,
        retry_stream: bool = True,
    ) -> None:
        self._client = client
        self._retry_policy = retry_policy
        self._enabled = enabled
        self._retry_stream = retry_stream

    async def send(self, request: HttpRequest) -> HttpResponse:
        if not self._enabled:
            return await self._client.send(request)
        return await self._retry_policy.execute(
            lambda: self._client.send(request)
        )

    @asynccontextmanager
    async def stream(
        self,
        request: HttpRequest,
    ) -> AsyncIterator[HttpResponse]:
        if not (self._enabled and self._retry_stream):
            async with self._client.stream(request) as response:
                yield response
            return

        async def _enter():
            cm = self._client.stream(request)
            response = await cm.__aenter__()
            return cm, response

        cm, response = await self._retry_policy.execute(_enter)
        try:
            yield response
        finally:
            await cm.__aexit__(None, None, None)

    async def aclose(self) -> None:
        await self._client.aclose()
