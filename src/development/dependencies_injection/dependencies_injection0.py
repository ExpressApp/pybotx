from uuid import UUID

from botx import Bot, Depends, Message

bot = Bot()


def get_user_huid(message: Message) -> UUID:
    return message.user_huid


@bot.handler
async def my_handler(user_huid: UUID = Depends(get_user_huid)) -> None:
    print(f"Message from {user_huid}")
