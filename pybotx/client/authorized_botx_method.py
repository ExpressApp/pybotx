from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncGenerator
import warnings

import httpx

from pybotx.auth import BotXAuthVersion
from pybotx.client.botx_method import BotXMethod, response_exception_thrower
from pybotx.client.exceptions.common import InvalidBotAccountError
from pybotx.client.get_token import get_token


class AuthorizedBotXMethod(BotXMethod):
    status_handlers = {401: response_exception_thrower(InvalidBotAccountError)}
    _legacy_auth_warned: bool = False

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

    async def _add_authorization_headers(self, headers: dict[str, Any]) -> None:
        auth_version = self._bot_accounts_storage.get_auth_version()
        if auth_version == BotXAuthVersion.V2:
            token = self._bot_accounts_storage.build_jwt_v2(self._bot_id)
        elif auth_version == BotXAuthVersion.V1:
            if not self._legacy_auth_warned:
                warnings.warn(
                    "BotX auth v1 is deprecated; use auth_version=BotXAuthVersion.V2",
                    DeprecationWarning,
                    stacklevel=2,
                )
                self._legacy_auth_warned = True
            token_or_none = self._bot_accounts_storage.get_token_or_none(self._bot_id)
            if token_or_none is None:
                token = await get_token(
                    self._bot_id,
                    self._httpx_client,
                    self._bot_accounts_storage,
                )
                self._bot_accounts_storage.set_token(self._bot_id, token)
            else:
                token = token_or_none
        else:
            raise NotImplementedError(f"Unsupported auth version: {auth_version}")

        headers.update({"Authorization": f"Bearer {token}"})
