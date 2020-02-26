from botx import Bot

from bot.middleware import FSMMiddleware

bot = Bot()
bot.add_middleware(FSMMiddleware, bot=bot, states=states)
