from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pybotx.bot.bot import Bot


@asynccontextmanager
async def lifespan_wrapper(bot: Bot) -> AsyncGenerator[Bot, None]:
    await bot.startup()

    try:
        yield bot
    finally:
        await bot.shutdown()
