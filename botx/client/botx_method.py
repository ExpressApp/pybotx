from typing import Any, Awaitable, Callable, Mapping, NoReturn, Type, TypeVar
from urllib.parse import urljoin
from uuid import UUID

import httpx
from pydantic import ValidationError

from botx.shared_models.api_base import APIBaseModel
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.exceptions import (
    ExceptionNotRaisedInStatusHandlerError,
    InvalidBotXResponseError,
    InvalidBotXStatusCodeError,
)

StatusHandlers = Mapping[  # noqa: WPS221  (StatusHandler used only in this Mapping)
    int,
    Callable[[httpx.Response], NoReturn],
]

TBotXAPIModel = TypeVar("TBotXAPIModel", bound=APIBaseModel)


class BotXMethod:
    status_handlers: StatusHandlers = {}

    def __init__(
        self,
        sender_bot_id: UUID,
        httpx_client: httpx.AsyncClient,
        bot_accounts_storage: BotAccountsStorage,
    ) -> None:
        self._bot_id = sender_bot_id
        self._httpx_client = httpx_client
        self._bot_accounts_storage = bot_accounts_storage

    # For MyPy checks
    execute: Callable[..., Awaitable[Any]]

    async def execute(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        raise NotImplementedError("You should define `execute` method")

    def _build_url(self, path: str) -> str:
        host = self._bot_accounts_storage.get_host(self._bot_id)
        return urljoin(f"https://{host}", path)

    def _extract_api_model(
        self,
        model_cls: Type[TBotXAPIModel],
        response: httpx.Response,
    ) -> TBotXAPIModel:
        try:
            return model_cls.parse_raw(response.content)
        except ValidationError as exc:
            raise InvalidBotXResponseError(response) from exc

    async def _botx_method_call(self, *args: Any, **kwargs: Any) -> httpx.Response:
        response = await self._httpx_client.request(*args, **kwargs)

        handler = self.status_handlers.get(response.status_code)
        if handler:
            handler(response)
            raise ExceptionNotRaisedInStatusHandlerError(
                response.status_code,
                handler.__name__,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise InvalidBotXStatusCodeError(exc.response)

        return response
