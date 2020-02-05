from botx import Bot, Message

bot = Bot()


@bot.exception_handler(RuntimeError)
async def error_handler(exc: Exception, msg: Message) -> None:
    await msg.bot.answer_message(f"Error occurred during handling command: {exc}", msg)


@bot.handler
async def handler_with_bug(message: Message) -> None:
    raise RuntimeError(message.body)
