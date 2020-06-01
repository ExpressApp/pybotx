import pprint
from collections import defaultdict
from enum import Enum, auto
from typing import DefaultDict, Dict
from uuid import UUID

from bot.middleware import FSM, FlowError
from botx import Message


class FSMStates(Enum):
    get_first_name = auto()
    get_middle_name = auto()
    get_last_name = auto()
    get_age = auto()
    get_gender = auto()
    end = auto()


fsm = FSM(FSMStates)
user_info: DefaultDict[UUID, Dict[str, str]] = defaultdict(dict)


@fsm.handler(on_state=FSMStates.get_first_name, next_state=FSMStates.get_middle_name)
async def get_first_name(message: Message) -> None:
    user_info[message.user_huid]["first_name"] = message.body
    await message.bot.answer_message("enter middle name", message)


@fsm.handler(on_state=FSMStates.get_middle_name, next_state=FSMStates.get_last_name)
async def get_middle_name(message: Message) -> None:
    user_info[message.user_huid]["middle_name"] = message.body
    await message.bot.answer_message("enter last name", message)


@fsm.handler(
    on_state=FSMStates.get_last_name,
    next_state=FSMStates.get_age,
    on_failure=FSMStates.get_first_name,
)
async def get_last_name(message: Message) -> None:
    if message.body == "fail":
        await message.bot.answer_message("failed to read last name", message)
        raise FlowError

    await message.bot.answer_message("enter age", message)
    user_info[message.user_huid]["last_name"] = message.body


@fsm.handler(on_state=FSMStates.get_age, next_state=FSMStates.get_gender)
async def get_age(message: Message) -> None:
    await message.bot.answer_message("enter gender", message)
    user_info[message.user_huid]["age"] = message.body


@fsm.handler(on_state=FSMStates.get_gender, next_state=None)
async def get_gender(message: Message) -> None:
    user_info[message.user_huid]["gender"] = message.body
    await message.bot.answer_message("thanks for sharing info:", message)
    await message.bot.answer_message(pprint.pformat(user_info), message)
