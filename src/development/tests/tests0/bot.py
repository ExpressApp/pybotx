from botx import Bot, Message

bot = Bot()


@bot.handler
async def hello(message: Message) -> None:
    await bot.answer_message(f"Hello, {message.user.username}", message)
