import asyncio
from dataclasses import dataclass
from uuid import UUID

from botx import Bot, Depends, Message


@dataclass
class User:
    user_huid: UUID
    username: str


bot = Bot()


def get_user_huid_from_message(message: Message) -> UUID:
    return message.user_huid


async def fetch_user_by_huid(
    user_huid: UUID = Depends(get_user_huid_from_message),
) -> User:
    # some operations with db for example
    await asyncio.sleep(0.5)
    return User(user_huid=user_huid, username="Requested User")


@bot.handler
def my_handler(user: User = Depends(fetch_user_by_huid)) -> None:
    print(f"Message from {user.username}")
