from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

import httpx

from pybotx.client.botx_method import BotXMethod, response_exception_thrower
from pybotx.client.exceptions.common import InvalidBotAccountError
from pybotx.client.get_token import get_token


class AuthorizedBotXMethod(BotXMethod):
    status_handlers = {401: response_exception_thrower(InvalidBotAccountError)}

    async def _botx_method_call(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        await self._add_authorization_headers(headers)

        return await super()._botx_method_call(*args, headers=headers, **kwargs)

    @asynccontextmanager
    async def _botx_method_stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[httpx.Response, None]:
        headers = kwargs.pop("headers", {})
        await self._add_authorization_headers(headers)

        async with super()._botx_method_stream(
            *args,
            headers=headers,
            **kwargs,
        ) as response:
            yield response

    async def _add_authorization_headers(self, headers: Dict[str, Any]) -> None:
        token = self._bot_accounts_storage.get_token_or_none(self._bot_id)
        if not token:
            token = await get_token(
                self._bot_id,
                self._httpx_client,
                self._bot_accounts_storage,
            )
            self._bot_accounts_storage.set_token(self._bot_id, token)

        headers.update({"Authorization": f"Bearer {token}"})
