"""Definition for middleware that precess next step handlers logic."""

import contextlib
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from uuid import UUID

from loguru import logger
from pydantic import BaseConfig, BaseModel

from botx import Bot, Collector, concurrency, converters, exceptions
from botx.collecting.handlers.handler import Handler
from botx.collecting.handlers.name_generators import get_name_from_callable
from botx.dependencies.models import Depends
from botx.middlewares.base import BaseMiddleware
from botx.models.messages.message import Message
from botx.typing import Executor


class NextStepHandlerState(BaseModel):
    """Information about next step handler."""

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    #: name of handler that should be called.
    name: str

    #: arguments that should be set on message for handler.
    arguments: Dict[str, Any]


class NextStepMiddleware(BaseMiddleware):
    """
    Naive next step handlers middleware. May be useful in simple apps or as base.

    Important:
        This middleware should be the last included into bot, since it will break
        execution if right handler will be found.
    """

    def __init__(  # noqa: WPS211
        self,
        executor: Executor,
        bot: Bot,
        functions: Union[Dict[str, Callable], Sequence[Callable]],
        break_handler: Optional[Union[Handler, str, Callable]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> None:
        """Init middleware with required query_params.

        Arguments:
            executor: next callable that should be executed.
            bot: bot that will store ns state.
            functions: dict of functions and their names that will be used as next step
                handlers or set of sequence of functions that will be registered by
                their names.
            break_handler: handler instance or name of handler that will break next step
                handlers chain.
            dependencies: background dependencies that should be applied to handlers.
            dependency_overrides_provider: object that will override dependencies for
                this handler.
        """
        super().__init__(executor)

        dependencies = converters.optional_sequence_to_list(
            bot.collector.dependencies,
        ) + converters.optional_sequence_to_list(
            dependencies,
        )  # noqa: W503
        dep_override = (
            dependency_overrides_provider or bot.collector.dependency_overrides_provider
        )
        bot.state.ns_collector = Collector(
            dependencies=dependencies,
            dependency_overrides_provider=dep_override,
        )
        bot.state.ns_store = {}

        bot.state.ns_break_handler = None
        if break_handler:
            if isinstance(break_handler, Handler):
                bot.state.ns_collector.handlers.append(break_handler)
                bot.state.ns_break_handler = break_handler.name
            elif callable(break_handler):
                register_function_as_ns_handler(bot, break_handler)
                bot.state.ns_break_handler = get_name_from_callable(break_handler)
            else:
                bot.state.ns_collector.handlers.append(
                    bot.collector.handler_for(break_handler),
                )
                bot.state.ns_break_handler = break_handler

        if isinstance(functions, dict):
            functions_dict = functions
        else:
            functions_dict = {get_name_from_callable(func): func for func in functions}

        for name, function in functions_dict.items():
            register_function_as_ns_handler(bot, function, name)

    async def dispatch(self, message: Message, call_next: Executor) -> None:
        """Execute middleware logic.

        Arguments:
            message: incoming message.
            call_next: next executor in middleware chain.
        """
        if message.bot.state.ns_break_handler:
            break_handler = message.bot.state.ns_collector.handler_for(
                message.bot.state.ns_break_handler,
            )
            if break_handler.matches(message):
                await self.drop_next_step_handlers_chain(message)
                await break_handler(message)
                return

        try:
            next_handler, state = await self.lookup_next_handler_for_message(message)
        except (exceptions.NoMatchFound, IndexError, KeyError, RuntimeError):
            await concurrency.callable_to_coroutine(call_next, message)
            return

        key = get_chain_key_by_message(message)
        logger.bind(botx_ns_middleware=True, payload={"next_step_key": key}).info(
            "botx: found next step handler",
        )

        for state_argument in state.arguments.items():
            setattr(message.state, state_argument[0], state_argument[1])
        await next_handler(message)

    async def lookup_next_handler_for_message(
        self,
        message: Message,
    ) -> Tuple[Handler, NextStepHandlerState]:
        """Find handler in bot storage or in handlers.

        Arguments:
            message: message for which next step handler should be found.

        Returns:
            Found handler and state with arguments for message.
        """
        handlers: List[NextStepHandlerState] = message.bot.state.ns_store[
            get_chain_key_by_message(message)
        ]
        handler_state = handlers.pop()
        return (
            message.bot.state.ns_collector.handler_for(handler_state.name),
            handler_state,
        )

    async def drop_next_step_handlers_chain(self, message: Message) -> None:
        """Drop registered chain for message.

        Arguments:
            message: message for which chain should be dropped.
        """
        with contextlib.suppress(KeyError):
            message.bot.state.ns_store.pop(get_chain_key_by_message(message))


def get_chain_key_by_message(message: Message) -> Tuple[str, UUID, UUID, UUID]:
    """Generate key for next step handlers chain from message.

    Arguments:
        message: message from which key should be generated.

    Returns:
        Key using which handler should be found.

    Raises:
        RuntimeError: raised if key for chain can not be built.
    """
    # key is a tuple of (host, bot_id, chat_id, user_huid)
    if message.user_huid is None:
        raise RuntimeError("key for chain can be obtained only for messages from users")
    return message.host, message.bot_id, message.group_chat_id, message.user_huid


def register_function_as_ns_handler(
    bot: Bot,
    func: Callable,
    name: Optional[str] = None,
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

    Raises:
        ValueError: raised if there is error to register handler.
    """
    name = name or get_name_from_callable(func)
    collector: Collector = bot.state.ns_collector
    try:
        collector.add_handler(
            body=name,
            name=name,
            handler=func,
            include_in_status=False,
            dependencies=collector.dependencies,
            dependency_overrides_provider=collector.dependency_overrides_provider,
        )
    except AssertionError as exc:
        raise ValueError(exc.args)


def register_next_step_handler(
    message: Message,
    func: Union[str, Callable],
    **ns_arguments: Any,
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

    Raises:
        ValueError: raised if passed message does not include user_huid or if handler
            that should be registered as next step does not exists.
    """
    if message.user_huid is None:
        raise ValueError(
            "message for which ns handler is registered should include user_huid",
        )

    bot = message.bot
    collector: Collector = bot.state.ns_collector
    name = get_name_from_callable(func) if callable(func) else func

    try:
        collector.handler_for(name)
    except exceptions.NoMatchFound:
        raise ValueError(
            "bot does not have registered next step handler with name {0}".format(name),
        )

    key = get_chain_key_by_message(message)

    store: List[NextStepHandlerState] = bot.state.ns_store.setdefault(key, [])
    store.append(NextStepHandlerState(name=name, arguments=ns_arguments))
