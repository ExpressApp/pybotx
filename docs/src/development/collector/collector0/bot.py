from botx import Bot

from .a_commands import collector

bot = Bot()
bot.include_collector(collector)


@bot.default(include_in_status=False)
async def default_handler() -> None:
    print("default handler")
