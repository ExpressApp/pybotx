import asyncio

from botx import Bot, HandlerCollector, lifespan_wrapper

# Не забудьте заполнить учётные данные бота
built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])


async def main() -> None:
    async with lifespan_wrapper(built_bot) as bot:
        for bot_account in bot.bot_accounts:
            token = await built_bot.get_token(bot_id=bot_account.id)
            print(token)  # noqa: WPS421


if __name__ == "__main__":
    asyncio.run(main())
