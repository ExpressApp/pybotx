import asyncio
import json
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union
from weakref import WeakSet

from pydantic import ValidationError, parse_obj_as

from botx.bot.api.commands.commands import BotAPICommand
from botx.bot.api.status.recipient import BotAPIStatusRecipient
from botx.bot.api.status.response import build_bot_status_response
from botx.bot.handler import Middleware
from botx.bot.handler_collector import HandlerCollector
from botx.bot.models.commands.commands import BotCommand
from botx.bot.models.status.bot_menu import BotMenu
from botx.bot.models.status.recipient import StatusRecipient


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        middlewares: Optional[List[Middleware]] = None,
    ) -> None:
        self._middlewares = middlewares or []
        self._handler_collector = self._merge_collectors(collectors)
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

    async def shutdown(self) -> None:
        if not self._tasks:
            return  # pragma: no cover

        finished_tasks, _ = await asyncio.wait(
            self._tasks,
            return_when=asyncio.ALL_COMPLETED,
        )

        # Raise handlers exceptions
        for task in finished_tasks:
            task.result()

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
