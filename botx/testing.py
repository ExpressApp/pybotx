from contextlib import asynccontextmanager
from typing import AsyncGenerator

from botx.bot import Bot


@asynccontextmanager
async def lifespan_wrapper(bot: Bot) -> AsyncGenerator[Bot, None]:
    try:
        yield bot
    finally:
        await bot.shutdown()
