from typing import Callable
from unittest.mock import Mock

import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    IncomingMessageHandlerFunc,
    Middleware,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__middlewares__correct_order(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    middlewares_called_order = []
    user_command = incoming_message_factory(body="/command")

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            # middlewares_called_order is already accessible in this scope
            middlewares_called_order.append(number)

            await call_next(message, bot)

        return middleware

    collector = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector.command(
        "/command",
        description="My command",
        middlewares=[middleware_factory(5), middleware_factory(6)],
    )
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()

    assert middlewares_called_order == [1, 2, 3, 4, 5, 6]


async def test__middlewares__called_in_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    middlewares_called_order = []
    user_command = incoming_message_factory(body="/command")

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            # middlewares_called_order is already accessible in this scope
            middlewares_called_order.append(number)

            await call_next(message, bot)

        return middleware

    collector = HandlerCollector(
        middlewares=[middleware_factory(3), middleware_factory(4)],
    )

    @collector.default_message_handler(
        middlewares=[middleware_factory(5), middleware_factory(6)],
    )
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        middlewares=[middleware_factory(1), middleware_factory(2)],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2, 3, 4, 5, 6]


async def test__middlewares__correct_child_collector_middlewares(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    middlewares_called_order = []
    user_command = incoming_message_factory(body="/command")

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            # middlewares_called_order is already accessible in this scope
            middlewares_called_order.append(number)

            await call_next(message, bot)

        return middleware

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
    built_bot = Bot(collectors=[collector_1], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2, 3, 4]


async def test__middlewares__correct_parent_collector_middlewares(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    middlewares_called_order = []
    user_command = incoming_message_factory(body="/command")

    def middleware_factory(number: int) -> Middleware:
        async def middleware(
            message: IncomingMessage,
            bot: Bot,
            call_next: IncomingMessageHandlerFunc,
        ) -> None:
            nonlocal middlewares_called_order
            middlewares_called_order.append(number)

            await call_next(message, bot)

        return middleware

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
    built_bot = Bot(collectors=[collector_1], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert middlewares_called_order == [1, 2]
