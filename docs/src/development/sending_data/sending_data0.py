from uuid import UUID

from botx import Bot, SendingMessage

bot = Bot()
CHAT_ID = UUID("1f972f5e-6d17-4f39-be5b-f7e20f1b4d13")
BOT_ID = UUID("cc257e1c-c028-4181-a055-01e14ba881b0")
CTS_HOST = "my-cts.example.com"


async def some_function() -> None:
    message = SendingMessage(
        text="You were chosen by random.",
        bot_id=BOT_ID,
        host=CTS_HOST,
        chat_id=CHAT_ID,
    )
    await bot.send(message)
