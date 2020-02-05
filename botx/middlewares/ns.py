"""Definition for middleware that precess next step handlers logic."""

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from uuid import UUID

from loguru import logger

from botx import bots
from botx.collecting import Handler
from botx.concurrency import callable_to_coroutine
from botx.exceptions import NoMatchFound
from botx.middlewares.base import BaseMiddleware
from botx.models import messages
from botx.typing import Executor
from botx.utils import get_name_from_callable


class NextStepMiddleware(BaseMiddleware):
    """
    Naive next step handlers middleware. May be useful in simple apps or as base.

    Important:
        This middleware should be the last included into bot, since it will break
        execution if right handler will be found.

    """

    def __init__(
        self,
        executor: Executor,
        bot: bots.Bot,
        functions: Union[Dict[str, Callable], Sequence[Callable]],
        break_handler: Optional[Union[Handler, str]] = None,
    ) -> None:
        """Init middleware with required params.

        Arguments:
            executor: next callable that should be executed.
            bot: bot that will store ns state.
            functions: dict of functions and their names that will be used as next step
                handlers or set of sequence of functions that will be registered by
                their names.
            break_handler: handler instance or name of handler that will break next step
                handlers chain.
        """
        super().__init__(executor)
        self.break_handler: Optional[Handler] = None
        """Handler that will be used if there is a break chain message."""
        if break_handler:
            self.break_handler = (
                break_handler
                if isinstance(break_handler, Handler)
                else bot.handler_for(break_handler)
            )
        bot.state.ns_storage = {}
        bot.state.ns_handlers = {}
        bot.state.ns_arguments = {}
        if isinstance(functions, dict):
            functions_dict = functions
        else:
            functions_dict = {get_name_from_callable(func): func for func in functions}

        for name, function in functions_dict.items():
            register_function_as_ns_handler(bot, function, name)

    async def dispatch(self, message: messages.Message, call_next: Executor) -> None:
        """Execute middleware logic.

        Arguments:
            message: incoming message.
            call_next: next executor in middleware chain.
        """
        if self.break_handler and self.break_handler.matches(message):
            await self.drop_next_step_handlers_chain(message)
            await self.break_handler(message)
            return

        try:
            next_handler = await self.lookup_next_handler_for_message(message)
        except (NoMatchFound, IndexError, KeyError, RuntimeError):
            await callable_to_coroutine(call_next, message)
            return

        key = get_chain_key_by_message(message)
        logger.bind(botx_ns_middleware=True, payload={"next_step_key": key}).info(
            "botx: found next step handler"
        )

        arguments_lists = message.bot.state.ns_arguments[key]
        arguments = arguments_lists.pop()
        for argument, argument_value in arguments.items():
            setattr(message.state, argument, argument_value)
        await next_handler(message)

    async def lookup_next_handler_for_message(
        self, message: messages.Message
    ) -> Handler:
        """Find handler in bot storage or in handlers.

        Arguments:
            message: message for which next step handler should be found.

        Returns:
            Found handler.
        """
        handlers: List[str] = message.bot.state.ns_storage[
            get_chain_key_by_message(message)
        ]
        handler_name = handlers.pop()
        try:
            return message.bot.state.ns_handlers[handler_name]
        except KeyError:
            return message.bot.handler_for(handler_name)

    async def drop_next_step_handlers_chain(self, message: messages.Message) -> None:
        """Drop registered chain for message.

        Arguments:
            message: message for which chain should be dropped.
        """
        message.bot.state.ns_storage.pop(get_chain_key_by_message(message))


def get_chain_key_by_message(message: messages.Message) -> Tuple[str, UUID, UUID, UUID]:
    """Generate key for next step handlers chain from message.

    Arguments:
        message: message from which key should be generated.

    Returns:
        Key using which handler should be found.
    """
    # key is a tuple of (host, bot_id, chat_id, user_huid)
    if message.user_huid is None:
        raise RuntimeError("Key for chain can be obtained only for messages from users")
    return message.host, message.bot_id, message.group_chat_id, message.user_huid


def register_function_as_ns_handler(
    bot: bots.Bot, func: Callable, name: Optional[str] = None
) -> None:
    """Register new function that can be called as next step handler.

    !!! warning
        This functions should not be called to dynamically register new functions in
        handlers or elsewhere, since state on different time can be changed somehow.

    Arguments:
        bot: bot that stores ns state.
        func: functions that will be called as ns handler. Will be transformed to
            coroutine if it is not already.
        name: name for new function. Will be generated from `func` if not passed.
    """
    name = name or get_name_from_callable(func)
    handlers = bot.state.ns_handlers
    if name in handlers:
        raise ValueError(f"bot ns functions already include function with {name}")
    handlers[name] = Handler(
        body="",
        handler=func,
        include_in_status=False,
        dependencies=bot.collector.dependencies,
        dependency_overrides_provider=bot.dependency_overrides,
    )


def register_next_step_handler(
    message: messages.Message, func: Union[str, Callable], **ns_arguments: Any
) -> None:
    """Register new next step handler for next message from user.

    !!! info
        While registration handler for next message this function fill first try to find
        handlers that were registered using `register_function_as_ns_handler`, then
        handlers that are registered in bot itself and then if no one was found an
        exception will be raised.

    Arguments:
        message: incoming message.
        func: function name of function which name will be retrieved to register next
            handler.
        ns_arguments: arguments that will be stored in message state while executing
            handler with next message.
    """
    if message.user_huid is None:
        raise ValueError(
            "message for which ns handler is registered should include user_huid"
        )

    bot = message.bot
    handlers = bot.state.ns_handlers
    name = get_name_from_callable(func) if callable(func) else func

    try:
        bot.handler_for(name)
    except NoMatchFound:
        if name not in handlers:
            raise ValueError(
                f"bot does not have registered function or handler with name {name}"
            )

    key = get_chain_key_by_message(message)

    store: List[str] = bot.state.ns_storage.setdefault(key, [])
    args: List[dict] = bot.state.ns_arguments.setdefault(key, [])

    store.append(name)
    args.append(ns_arguments)
