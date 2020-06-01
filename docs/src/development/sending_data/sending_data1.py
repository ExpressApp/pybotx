from botx import Bot, Message, SendingMessage

bot = Bot()


@bot.handler(command="/my-handler")
async def some_handler(message: Message) -> None:
    message = SendingMessage.from_message(
        text="You were chosen by random.", message=message,
    )
    await bot.send(message)
