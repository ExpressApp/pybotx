import asyncio
from dataclasses import dataclass
from uuid import UUID

from botx import Bot, Collector
from botx import DependencyFailure
from botx import Depends
from botx import Message


@dataclass
class User:
    user_huid: UUID
    username: str
    is_authenticated: bool


collector = Collector()


def get_user_huid_from_message(message: Message) -> UUID:
    return message.user_huid


async def fetch_user_by_huid(
    user_huid: UUID = Depends(get_user_huid_from_message),
) -> User:
    # some operations with db for example
    await asyncio.sleep(0.5)
    return User(user_huid=user_huid, username="Requested User", is_authenticated=False)


async def authenticate_user(
    bot: Bot, message: Message, user: User = Depends(fetch_user_by_huid)
) -> None:
    if not user.is_authenticated:
        await bot.answer_message("You should login first", message)
        raise DependencyFailure


@collector.handler(dependencies=[Depends(authenticate_user)])
def my_handler(user: User = Depends(fetch_user_by_huid)) -> None:
    print(f"Message from {user.username}")
