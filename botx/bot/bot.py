import asyncio
from typing import Any, Dict, List, Optional, Sequence, Type
from uuid import UUID
from weakref import WeakSet

import httpx
from pydantic import ValidationError, parse_obj_as

from botx.bot.api.commands.commands import BotAPICommand
from botx.bot.api.status.recipient import BotAPIStatusRecipient
from botx.bot.api.status.response import build_bot_status_response
from botx.bot.credentials_storage import CredentialsStorage
from botx.bot.handler import Middleware
from botx.bot.handler_collector import HandlerCollector
from botx.bot.middlewares.exceptions import ExceptionHandler, ExceptionMiddleware
from botx.bot.models.commands.commands import BotCommand
from botx.bot.models.commands.enums import ChatTypes
from botx.bot.models.credentials import BotCredentials
from botx.bot.models.status.bot_menu import BotMenu
from botx.bot.models.status.recipient import StatusRecipient
from botx.client.botx_api_client import BotXAPIClient
from botx.converters import optional_sequence_to_list


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        credentials: Sequence[BotCredentials],
        middlewares: Optional[Sequence[Middleware]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._middlewares = optional_sequence_to_list(middlewares)
        self._add_exception_middleware()

        self._handler_collector = self._merge_collectors(collectors)

        self._botx_api_client = BotXAPIClient(
            httpx_client,
            CredentialsStorage(list(credentials)),
        )

        # Can't set WeakSet[asyncio.Task] type in Python < 3.9
        self._tasks = WeakSet()  # type: ignore

    def async_execute_raw_bot_command(self, raw_bot_command: Dict[str, Any]) -> None:
        try:
            bot_api_command: BotAPICommand = parse_obj_as(
                # Same ignore as in pydantic
                BotAPICommand,  # type: ignore[arg-type]
                raw_bot_command,
            )
        except ValidationError as validation_exc:
            raise ValueError("Bot command validation error") from validation_exc

        bot_command = bot_api_command.to_domain(raw_bot_command)
        self.async_execute_bot_command(bot_command)

    def async_execute_bot_command(self, bot_command: BotCommand) -> None:
        task = asyncio.create_task(
            self._handler_collector.handle_bot_command(bot_command, self),
        )
        self._tasks.add(task)

    async def raw_get_status(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        try:
            bot_api_status_recipient = BotAPIStatusRecipient.parse_obj(query_params)
        except ValidationError as exc:
            raise ValueError("Status request validation error") from exc

        status_recipient = bot_api_status_recipient.to_domain()

        bot_menu = await self.get_status(status_recipient)
        return build_bot_status_response(bot_menu)

    def add_exception_handler(
        self,
        exc_class: Type[Exception],
        handler: ExceptionHandler,
    ) -> None:
        self._exception_middleware.add_exception_handler(exc_class, handler)

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu:
        return await self._handler_collector.get_bot_menu(status_recipient, self)

    async def shutdown(self) -> None:
        await self._botx_api_client.shutdown()

        if not self._tasks:
            return  # pragma: no cover

        finished_tasks, _ = await asyncio.wait(
            self._tasks,
            return_when=asyncio.ALL_COMPLETED,
        )

        # Raise handlers exceptions
        for task in finished_tasks:
            task.result()

    async def create_chat(
        self,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        members: List[UUID],
        description: Optional[str] = None,
        shared_history: bool = False,
    ) -> UUID:
        return await self._botx_api_client.create_chat(
            bot_id,
            name,
            chat_type,
            members,
            description,
            shared_history,
        )

    async def get_token(self, bot_id: UUID) -> str:
        return await self._botx_api_client.get_token(bot_id)

    def _add_exception_middleware(self) -> None:
        exception_middleware = ExceptionMiddleware()
        self._exception_middleware = exception_middleware
        self._middlewares.insert(0, exception_middleware.dispatch)

    def _merge_collectors(
        self,
        collectors: Sequence[HandlerCollector],
    ) -> HandlerCollector:
        collectors_count = len(collectors)
        if collectors_count == 0:
            raise ValueError("Bot should have at least one `HandlerCollector`")

        main_collector = HandlerCollector(middlewares=self._middlewares)
        main_collector.include(*collectors)

        return main_collector
