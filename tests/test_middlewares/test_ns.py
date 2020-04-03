from collections import Counter

import pytest

from botx import (
    Bot,
    ChatCreatedEvent,
    Collector,
    IncomingMessage,
    Message,
    UserKinds,
    testing,
)
from botx.middlewares.ns import (
    NextStepMiddleware,
    register_function_as_ns_handler,
    register_next_step_handler,
)
from botx.models.events import UserInChatCreated
from botx.testing import MessageBuilder


def test_register_ns_middleware_using_functions_dict(bot: Bot) -> None:
    def test_function() -> None:
        ...  # pragma: no cover

    functions = {"ns_handler": test_function}

    bot.add_middleware(NextStepMiddleware, bot=bot, functions=functions)

    [bot.state.ns_collector.handler_for(name) for name in functions]


def test_register_ns_middleware_using_functions_set(bot: Bot) -> None:
    def test_function() -> None:
        ...  # pragma: no cover

    functions = {test_function}

    bot.add_middleware(NextStepMiddleware, bot=bot, functions=functions)

    assert [bot.state.ns_collector.handler_for(name) for name in ["test_function"]]


def test_no_duplicate_handlers_registration(bot: Bot) -> None:
    def test_function() -> None:
        ...  # pragma: no cover

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={})

    register_function_as_ns_handler(bot, test_function)

    with pytest.raises(ValueError):
        register_function_as_ns_handler(bot, test_function)


def test_register_break_handler_as_string(bot: Bot) -> None:
    @bot.handler(command="/break")
    async def break_handler() -> None:
        ...  # pragma: no cover

    bot.add_middleware(
        NextStepMiddleware, bot=bot, functions={}, break_handler="break_handler"
    )

    assert bot.state.ns_collector.handler_for("break_handler") == bot.handler_for(
        "break_handler"
    )


def test_register_break_handler_as_handler(bot: Bot) -> None:
    @bot.handler(command="/break")
    async def break_handler() -> None:
        ...  # pragma: no cover

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={},
        break_handler=bot.handler_for("break_handler"),
    )

    assert bot.state.ns_collector.handler_for("break_handler") == bot.handler_for(
        "break_handler"
    )


def test_register_break_handler_as_function(bot: Bot) -> None:
    async def break_handler() -> None:
        ...  # pragma: no cover

    bot.add_middleware(
        NextStepMiddleware, bot=bot, functions={}, break_handler=break_handler,
    )

    assert bot.state.ns_collector.handler_for("break_handler").handler == break_handler


@pytest.mark.asyncio
async def test_error_if_trying_to_register_ns_for_not_registered_function(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    exc_raised = False

    @bot.handler(command="/start-ns")
    def chain_start(message: Message) -> None:
        try:
            register_next_step_handler(message, "some_function_name")
        except ValueError:
            nonlocal exc_raised
            exc_raised = True

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={})

    with testing.TestClient(bot) as client:
        incoming_message.command.body = "/start-ns"
        await client.send_command(incoming_message)
        assert exc_raised


@pytest.mark.asyncio
async def test_error_if_trying_to_register_ns_from_message_without_user_huid(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    exc_raised = False

    builder = MessageBuilder()
    builder.bot_id = incoming_message.bot_id
    builder.command_data = ChatCreatedEvent(
        group_chat_id=incoming_message.user.group_chat_id,
        chat_type=incoming_message.user.chat_type,
        name="chat",
        creator=incoming_message.user.user_huid,
        members=[
            UserInChatCreated(
                huid=incoming_message.user.user_huid,
                user_kind=UserKinds.user,
                name=incoming_message.user.username,
                admin=True,
            ),
            UserInChatCreated(
                huid=incoming_message.bot_id,
                user_kind=UserKinds.bot,
                name="",
                admin=False,
            ),
        ],
    )
    builder.user.user_huid = (
        builder.user.ad_login
    ) = builder.user.ad_domain = builder.user.username = None
    builder.body = "system:chat_created"
    builder.system_command = True

    def some_function() -> None:
        ...  # pragma: no cover

    bot.collector = Collector()
    bot.exception_middleware.executor = bot.collector

    @bot.chat_created
    def chain_start(message: Message) -> None:
        try:
            register_next_step_handler(message, some_function)
        except ValueError:
            nonlocal exc_raised
            exc_raised = True

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={})

    with testing.TestClient(bot) as client:
        await client.send_command(builder.message)
        assert exc_raised


@pytest.mark.asyncio
async def test_executing_ns_handlers(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    commands_visited = Counter()

    @bot.handler(command="/start-ns")
    def chain_start(message: Message) -> None:
        commands_visited["chain_start"] += 1
        register_next_step_handler(message, "ns_handler")

    def ns_handler() -> None:
        commands_visited["ns_handler"] += 1

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={ns_handler})

    with testing.TestClient(bot) as client:
        incoming_message.command.body = "/start-ns"
        await client.send_command(incoming_message)
        assert commands_visited["chain_start"] == 1

        await client.send_command(incoming_message)
        assert commands_visited["chain_start"] == commands_visited["ns_handler"] == 1


@pytest.mark.asyncio
async def test_setting_args_from_ns_registration_into_state(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    message_state = None

    @bot.handler(command="/start-ns")
    def chain_start(message: Message) -> None:
        register_next_step_handler(message, "ns_handler", arg1=1, arg2="2", arg3=True)

    def ns_handler(message: Message) -> None:
        nonlocal message_state
        message_state = message.state

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={ns_handler})

    with testing.TestClient(bot) as client:
        incoming_message.command.body = "/start-ns"
        await client.send_command(incoming_message)
        await client.send_command(incoming_message)

        assert message_state.arg1 == 1
        assert message_state.arg2 == "2"
        assert message_state.arg3


@pytest.mark.asyncio
async def test_ns_chain_can_be_stopped_by_break_handler(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    commands_visited = Counter()

    @bot.handler(command="/break-handler")
    def break_handler():
        commands_visited["break_handler"] += 1

    @bot.handler(command="/start-ns")
    def chain_start(message: Message) -> None:
        commands_visited["chain_start"] += 1
        register_next_step_handler(message, "ns_handler")

    def ns_handler(message: Message) -> None:
        commands_visited["ns_handler"] += 1
        register_next_step_handler(message, "chain_start")

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={ns_handler},
        break_handler="break_handler",
    )

    with testing.TestClient(bot) as client:
        incoming_message.command.body = "/start-ns"
        await client.send_command(incoming_message)
        await client.send_command(incoming_message)
        await client.send_command(incoming_message)

        incoming_message.command.body = "/break-handler"
        await client.send_command(incoming_message)

        assert commands_visited["break_handler"] == 1
        assert commands_visited["chain_start"] == 2
        assert commands_visited["ns_handler"] == 1
