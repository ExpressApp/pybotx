from botx import Bot, Message

bot = Bot()


@bot.handler
async def my_handler(message: Message) -> None:
    with open("my_file.txt") as f:
        await bot.send_file(f, message.credentials)
