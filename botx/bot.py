import asyncio
import json
from json.decoder import JSONDecodeError
from typing import Sequence, Union
from weakref import WeakSet

from pydantic import ValidationError, parse_obj_as

from botx.api.bot_api.typing import BotAPICommand
from botx.handler_collector import HandlerCollector
from botx.typing import BotXCommand


class Bot:
    def __init__(self, *, collectors: Sequence[HandlerCollector]) -> None:
        self._handler_collector = self._merge_collectors(collectors)
        # Can't set WeakSet[asyncio.Task] type in Python < 3.9
        self._tasks = WeakSet()  # type: ignore

    def async_execute_raw_botx_command(self, payload: Union[str, bytes]) -> None:
        try:
            raw_botx_command = json.loads(payload)
        except JSONDecodeError as decoding_exc:
            raise ValueError("Error while decoding JSON") from decoding_exc

        try:
            botx_api_command: BotAPICommand = parse_obj_as(
                # Same ignore as in pydantic
                BotAPICommand,  # type: ignore[arg-type]
                raw_botx_command,
            )
        except ValidationError as validation_exc:
            raise ValueError("Error validation BotX command") from validation_exc

        botx_command = botx_api_command.to_domain(raw_botx_command)

        self.async_execute_botx_command(botx_command)

    def async_execute_botx_command(self, botx_command: BotXCommand) -> None:
        task = asyncio.create_task(
            self._handler_collector.handle_botx_command(botx_command, self),
        )
        self._tasks.add(task)

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

        if collectors_count == 1:
            return collectors[0]

        collector = collectors[0]
        collector.include(*collectors[1:])
        return collector
