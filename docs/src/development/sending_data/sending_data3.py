from botx import Bot, File, Message, SendingMessage

bot = Bot()


@bot.handler
async def my_handler(message: Message) -> None:
    with open("my_file.txt") as f:
        notification = SendingMessage(
            file=File.from_file(f), credentials=message.credentials
        )

    await bot.send(notification)


@bot.handler
async def another_handler(message: Message) -> None:
    notification = SendingMessage.from_message(message=message)

    with open("my_file.txt") as f:
        notification.add_file(f)

    await bot.send(notification)
