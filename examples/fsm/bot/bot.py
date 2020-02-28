from typing import Any

from botx import Bot, ExpressServer, Message

from bot.config import BOT_SECRET, CTS_HOST
from bot.handlers import FSMStates, fsm
from bot.middleware import FlowError, FSMMiddleware, change_state

bot = Bot(known_hosts=[ExpressServer(host=CTS_HOST, secret_key=str(BOT_SECRET))])
bot.add_middleware(FSMMiddleware, bot=bot, fsm=fsm)


@bot.default(include_in_status=False)
async def default_handler(message: Message) -> None:
    if message.body == "start":
        change_state(message, FSMStates.get_first_name)
        await message.bot.answer_message("enter first name", message)
        return

    await message.bot.answer_message("default handler", message)


@bot.exception_handler(FlowError)
async def flow_error_handler(*_: Any) -> None:
    pass
