import pytest

from botx import Bot, Collector, Depends, IncomingMessage, SystemEvents, TestClient
from botx.collecting import Handler
from botx.exceptions import NoMatchFound
from tests.conftest import HandlerClass, handler_function


def test_collector_default_handler_generating() -> None:
    handler = Handler(
        body="/command",
        handler=handler_function,
        dependencies=[Depends(handler_function)],
    )

    collector = Collector(default=handler)

    assert collector.default_message_handler.handler == handler.handler
    assert collector.default_message_handler.body == handler.body
    assert collector.default_message_handler.dependencies == handler.dependencies


def test_only_one_handler_can_define_default_handler_when_merging(bot: Bot) -> None:
    handler = Handler(
        body="/command",
        handler=handler_function,
        dependencies=[Depends(handler_function)],
    )

    collector = Collector(default=handler)

    with pytest.raises(AssertionError):
        bot.include_collector(collector)


def test_error_when_merging_handlers_with_equal_bodies(bot: Bot) -> None:
    collector = Collector()
    collector.add_handler(body="/regular-handler", handler=handler_function)

    with pytest.raises(AssertionError):
        bot.include_collector(collector)


def test_error_when_merging_handlers_with_equal_names(bot: Bot) -> None:
    collector = Collector()
    collector.add_handler(
        body="/command1", name="regular_handler", handler=handler_function
    )

    with pytest.raises(AssertionError):
        bot.include_collector(collector)


def test_sorting_handlers_in_collector_by_body_length(bot: Bot) -> None:
    assert [handler.body for handler in bot.collector._added_handlers] == [
        "/regular-handler-that-excluded-from-status-by-callable-function",
        "/regular-handler-that-included-in-status-by-callable-function",
        "/regular-handler-that-excluded-from-status-and-auto-body",
        "/regular-handler-with-background-dependencies",
        "regular-handler-with-excluding-from-status",
        "/regular-handler-with-name",
        "system:chat_created",
        "/handler-command1",
        "/handler-command2",
        "/handler-command3",
        "/handler-command4",
        "/handler-command5",
        "/regular-handler",
        "/handler-command",
        "/default-handler",
        "/hidden-handler",
        "file_transfer",
    ]


def test_sorting_handlers_in_collector_by_body_length_when_merging(bot: Bot) -> None:
    collector = Collector()
    collector.add_handler(body="/" + "a" * 1000, handler=handler_function)

    bot.include_collector(collector)

    assert bot.collector._added_handlers[0].body == "/" + "a" * 1000


class TestGeneratingBodyFromHandler:
    def test_generating_from_camel_case(self, bot: Bot) -> None:
        bot.add_handler(handler=HandlerClass().HandlerMethodCamelCase)
        handler = bot.handler_for("HandlerMethodCamelCase")
        assert handler.body == "/handler-method-camel-case"

    def test_generating_from_pascal_case(self, bot: Bot) -> None:
        bot.add_handler(handler=HandlerClass().handlerMethodPascalCase)
        handler = bot.handler_for("handlerMethodPascalCase")
        assert handler.body == "/handler-method-pascal-case"

    def test_generating_from_snake_case(self, bot: Bot) -> None:
        bot.add_handler(handler=HandlerClass().handler_method_snake_case)
        handler = bot.handler_for("handler_method_snake_case")
        assert handler.body == "/handler-method-snake-case"


def test_raising_exception_when_searching_for_handler_and_no_found(bot: Bot) -> None:
    with pytest.raises(NoMatchFound):
        bot.handler_for("not-existing-handler")


class TestBuildingCommandForHandler:
    def test_error_when_no_args_passed(self, bot: Bot) -> None:
        with pytest.raises(TypeError):
            bot.command_for()

    def test_error_when_no_handler_found(self, bot: Bot) -> None:
        with pytest.raises(NoMatchFound):
            bot.command_for("not-existing-handler")

    def test_building_command_with_arguments(self, bot: Bot) -> None:
        assert (
            bot.command_for("regular_handler", "arg1", 1, True)
            == "/regular-handler arg1 1 True"
        )


def test_registration_handler_for_several_system_events() -> None:
    bot = Bot()
    bot.system_event(
        handler=handler_function,
        events=[SystemEvents.chat_created, SystemEvents.file_transfer],
    )
    only_events_bodies = all(
        handler.body
        in {SystemEvents.file_transfer.value, SystemEvents.chat_created.value}
        and handler.handler == handler_function
        for handler in bot.handlers
    )
    assert only_events_bodies


@pytest.mark.asyncio
async def test_executing_handler_when_found_full_matched_body(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    incoming_message.command.body = "/command"

    entered_into_command = False

    @bot.handler(command="/command")
    async def handler_for_command() -> None:
        nonlocal entered_into_command
        entered_into_command = True

    await client.send_command(incoming_message)

    assert entered_into_command


@pytest.mark.asyncio
async def test_executing_handler_when_found_partial_matched_body(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    incoming_message.command.body = "/command with arguments"

    entered_into_command = False

    @bot.handler(command="/command")
    async def handler_for_command() -> None:
        nonlocal entered_into_command
        entered_into_command = True

    await client.send_command(incoming_message)

    assert entered_into_command


def test_handler_can_not_consist_from_slashes_only(bot: Bot) -> None:
    with pytest.raises(AssertionError):

        @bot.handler(command="/////")
        def some_handler() -> None:
            pass  # pragma: no cover


def test_no_extra_space_on_command_built_through_command_for() -> None:
    handler = Handler(
        body="/command",
        handler=handler_function,
        dependencies=[Depends(handler_function)],
    )

    assert handler.command_for() == "/command"

    assert (
        handler.command_for(None, 1, "some string", True)
        == "/command 1 some string True"
    )


@pytest.mark.asyncio
async def test_dependencies_order_after_including_into_another_collector(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    incoming_message.command.body = "/command"

    args = []

    def first_dependency():
        args.append(1)

    def second_dependency():
        args.append(2)

    def third_dependency():
        args.append(3)

    first_collector = Collector(dependencies=[Depends(first_dependency)])
    second_collector = Collector(dependencies=[Depends(second_dependency)])

    @second_collector.handler(
        command="/command", dependencies=[Depends(third_dependency)]
    )
    async def handler_for_command() -> None:
        ...

    first_collector.include_collector(second_collector)
    bot.include_collector(first_collector)

    await client.send_command(incoming_message)

    assert args == [1, 2, 3]


@pytest.mark.asyncio
async def test_default_handler_after_including_into_another_collector() -> None:
    first_collector = Collector()
    second_collector = Collector()

    @second_collector.default
    async def default_handler() -> None:
        ...  # pragma: no cover

    first_collector.include_collector(second_collector)

    assert (
        first_collector.default_message_handler
        == second_collector.default_message_handler
    )
