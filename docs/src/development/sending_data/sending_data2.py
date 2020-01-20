from botx import Bot, Message

bot = Bot()


@bot.handler(command="/my-handler")
async def some_handler(message: Message) -> None:
    await bot.answer_message(text="VERY IMPORTANT NOTIFICATION!!!", message=message)
