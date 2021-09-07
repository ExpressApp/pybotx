from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from botx.typing import BotXCommand

if TYPE_CHECKING:
    from botx.bot import Bot

TBotXCommand = TypeVar("TBotXCommand", bound=BotXCommand)
HandlerFunc = Callable[[TBotXCommand, "Bot"], Awaitable[None]]


class BotXCommandHandler:
    def __init__(self, handler_func: HandlerFunc) -> None:  # type: ignore
        self.handler_func = handler_func

    async def __call__(self, botx_command: BotXCommand, bot: "Bot") -> None:
        await self.handler_func(botx_command, bot)
