from enum import Enum
from typing import Callable, Optional, Type, Dict, Tuple

from pydantic import BaseModel

from botx import Message
from botx.collecting import Handler
from botx.concurrency import callable_to_coroutine
from botx.middlewares.base import BaseMiddleware
from botx.typing import Executor


class Transition(BaseModel):
    on_failure: Optional[bool] = None
    on_success: Optional[bool] = None


class FSM:
    def __init__(self, states: Type[Enum]) -> None:
        self.handlers: Dict[Enum, Tuple[Transition, Handler]] = {}

    def handler(
            self,
            on_state: Optional[Enum] = None,
            next_state: Optional[Enum] = None,
            on_failure: Optional[Enum] = None,
    ) -> Callable:
        def decorator(handler: Callable) -> Callable:
            self.handlers[on_state] = (
                Transition(on_success=next_state, on_failure=on_failure),)

            return handler

        return decorator


def change_state(message: Message, new_state: Optional[Enum]) -> None:
    message.bot.state.fsm_state[message.user_huid] = new_state


class FSMMiddleware(BaseMiddleware):
    def __init__(self, executor: Executor, fsm: FSM) -> None:
        super().__init__(executor)
        self.fsm = fsm

    async def dispatch(self, message: Message, call_next: Executor) -> None:
        current_state = message.bot.state.fsm_state
        if current_state is not None:
            transitions, handler = self.fsm.handlers[current_state]
            try:
                await handler(message)
            except Exception as exc:
                if transitions.on_failure:
                    change_state(message, transitions.on_failure)
                raise exc
            else:
                if transitions.on_success:
                    change_state(message, transitions.on_success)
        else:
            await callable_to_coroutine(call_next, message)
