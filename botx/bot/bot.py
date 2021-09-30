import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID
from weakref import WeakSet

import httpx
from loguru import logger
from pydantic import ValidationError, parse_obj_as

from botx.bot.api.commands.commands import BotAPICommand
from botx.bot.api.status.recipient import BotAPIStatusRecipient
from botx.bot.api.status.response import build_bot_status_response
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.handler import Middleware
from botx.bot.handler_collector import HandlerCollector
from botx.bot.middlewares.exceptions import ExceptionHandlersDict, ExceptionMiddleware
from botx.bot.models.bot_account import BotAccount
from botx.bot.models.commands.commands import BotCommand
from botx.bot.models.status.bot_menu import BotMenu
from botx.bot.models.status.recipient import StatusRecipient
from botx.client.botx_api_client import BotXAPIClient
from botx.client.chats_api.list_chats import ChatListItem
from botx.client.exceptions import InvalidBotAccountError
from botx.converters import optional_sequence_to_list
from botx.shared_models.enums import ChatTypes


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        bot_accounts: Sequence[BotAccount],
        middlewares: Optional[Sequence[Middleware]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> None:
        self.state: SimpleNamespace = SimpleNamespace()

        self._middlewares = optional_sequence_to_list(middlewares)
        self._add_exception_middleware(exception_handlers)

        self._handler_collector = self._merge_collectors(collectors)

        self._bot_accounts_storage = BotAccountsStorage(list(bot_accounts))
        self._botx_api_client = BotXAPIClient(httpx_client, self._bot_accounts_storage)

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

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu:
        return await self._handler_collector.get_bot_menu(status_recipient, self)

    async def startup(self) -> None:
        for host, bot_id in self._bot_accounts_storage.iter_host_and_bot_id_pairs():
            try:
                token = await self.get_token(bot_id)
            except (InvalidBotAccountError, httpx.HTTPError):
                logger.warning(
                    "Can't get token for bot account: "
                    f"host - {host}, bot_id - {bot_id}",
                )
                continue

            self._bot_accounts_storage.set_token(bot_id, token)

    async def shutdown(self) -> None:
        await self._botx_api_client.shutdown()

        if not self._tasks:
            return

        finished_tasks, _ = await asyncio.wait(
            self._tasks,
            return_when=asyncio.ALL_COMPLETED,
        )

        # Raise handlers exceptions
        for task in finished_tasks:
            task.result()

    async def list_chats(
        self,
        bot_id: UUID,
    ) -> List[ChatListItem]:
        return await self._botx_api_client.list_chats(bot_id)

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

    async def send(self, body: str, *, bot_id: UUID, chat_id: UUID) -> UUID:
        return await self._botx_api_client.send_direct_notification(
            bot_id,
            body,
            chat_id,
        )

    def _add_exception_middleware(
        self,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> None:
        exception_middleware = ExceptionMiddleware(exception_handlers or {})
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
