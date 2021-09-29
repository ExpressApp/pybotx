from typing import Callable
from unittest.mock import Mock

import pytest

from botx import Bot, HandlerCollector, IncomingMessage, lifespan_wrapper
from botx.bot.handler import IncomingMessageHandlerFunc, Middleware


@pytest.mark.asyncio
async def test_middlewares_order(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    middlewares_called_order = []

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            middlewares_called_order.append(number)
            await call_next(message, bot)

        return middleware

    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector.command(
        "/command",
        description="My command",
        middlewares=[middleware_factory(5), middleware_factory(6)],
    )
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[],
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()

    assert middlewares_called_order == [1, 2, 3, 4, 5, 6]


@pytest.mark.asyncio
async def test_default_handler_middlewares(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    middlewares_called_order = []

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            middlewares_called_order.append(number)
            await call_next(message, bot)

        return middleware

    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[],
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_child_collector_middlewares(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    middlewares_called_order = []

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            middlewares_called_order.append(number)
            await call_next(message, bot)

        return middleware

    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector(
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    @collector_1.command("/other-command", description="My command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    collector_2 = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector_2.command("/command", description="My command")
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    collector_1.include(collector_2)
    built_bot = Bot(collectors=[collector_1], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_parent_collector_middlewares(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    middlewares_called_order = []

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            middlewares_called_order.append(number)
            await call_next(message, bot)

        return middleware

    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector(
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    @collector_1.command("/command", description="My command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    collector_2 = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector_2.command("/other-command", description="My command")
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    collector_1.include(collector_2)
    built_bot = Bot(collectors=[collector_1], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2]
