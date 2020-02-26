from enum import Enum, auto

from bot.middleware import FSM


class FSMStates(Enum):
    get_first_name = auto()
    get_middle_name = auto()
    get_last_name = auto()
    get_age = auto()
    get_gender = auto()


fsm = FSM(FSMStates)


@fsm.handler(on_state=FSMStates.get_first_name, next_state=FSMStates.get_middle_name)
async def get_first_name() -> None:
    pass


@fsm.handler(on_state=FSMStates.get_middle_name, next_state=FSMStates.get_last_name)
async def get_middle_name() -> None:
    pass


@fsm.handler(
    on_state=FSMStates.get_last_name,
    next_state=FSMStates.get_age,
    on_failure=FSMStates.get_first_name,
)
async def get_last_name() -> None:
    pass


@fsm.handler(on_state=FSMStates.get_age, next_state=FSMStates.get_gender)
async def get_age() -> None:
    pass


@fsm.handler(on_state=FSMStates.get_gender, next_state=None)
async def get_gender() -> None:
    pass
