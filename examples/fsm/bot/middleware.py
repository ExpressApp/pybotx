from dataclasses import dataclass
from enum import Enum
from typing import Callable
from typing import Dict
from typing import Final
from typing import Optional
from typing import Type
from typing import Union

from botx import Bot, Collector
from botx import Message
from botx.concurrency import callable_to_coroutine
from botx.middlewares.base import BaseMiddleware
from botx.typing import Executor

_default_transition: Final = object()


@dataclass
class Transition:
    on_failure: Optional[Union[Enum, object]] = _default_transition
    on_success: Optional[Union[Enum, object]] = _default_transition


class FlowError(Exception):
    pass


class FSM:
    def __init__(self, states: Type[Enum]) -> None:
        self.transitions: Dict[Enum, Transition] = {}
        self.collector = Collector()
        self.states = states

    def handler(
        self,
        on_state: Enum,
        next_state: Optional[Union[Enum, object]] = _default_transition,
        on_failure: Optional[Union[Enum, object]] = _default_transition,
    ) -> Callable:
        def decorator(handler: Callable) -> Callable:
            self.collector.add_handler(
                handler,
                body=on_state.name,
                name=on_state.name,
                include_in_status=False,
            )
            self.transitions[on_state] = Transition(
                on_success=next_state, on_failure=on_failure,
            )

            return handler

        return decorator


def change_state(message: Message, new_state: Optional[Enum]) -> None:
    message.bot.state.fsm_state[(message.user_huid, message.group_chat_id)] = new_state


class FSMMiddleware(BaseMiddleware):
    def __init__(
        self,
        executor: Executor,
        bot: Bot,
        fsm: FSM,
        initial_state: Optional[Enum] = None,
    ) -> None:
        super().__init__(executor)
        bot.state.fsm_state = {}
        self.fsm = fsm
        self.initial_state = initial_state
        for state in self.fsm.states:
            # check that for each state there is registered handler
            assert state in self.fsm.transitions

    async def dispatch(self, message: Message, call_next: Executor) -> None:
        current_state: Enum = message.bot.state.fsm_state.setdefault(
            (message.user_huid, message.group_chat_id), self.initial_state,
        )
        if current_state is not None:
            transition = self.fsm.transitions[current_state]
            handler = self.fsm.collector.handler_for(current_state.name)
            try:
                await handler(message)
            except Exception as exc:
                if transition.on_failure is not _default_transition:
                    change_state(message, transition.on_failure)
                raise exc
            else:
                if transition.on_success is not _default_transition:
                    change_state(message, transition.on_success)
        else:
            await callable_to_coroutine(call_next, message)
