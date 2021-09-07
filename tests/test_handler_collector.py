import pytest

from botx import Bot, ChatCreatedEvent, HandlerCollector, IncomingMessage


@pytest.fixture
def collector() -> HandlerCollector:
    return HandlerCollector()


def test_define_command_with_space(collector: HandlerCollector) -> None:
    # - Arrange -
    with pytest.raises(ValueError) as exc:

        @collector.handler(command="/ command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "include space" in str(exc)


def test_define_command_without_leading_slash(collector: HandlerCollector) -> None:
    # - Arrange -
    with pytest.raises(ValueError) as exc:

        @collector.handler(command="command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "should start with '/'" in str(exc)


def test_define_two_handlers_with_same_command(collector: HandlerCollector) -> None:
    # - Arrange -
    @collector.handler(command="/command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.handler(command="/command")
        async def handler_2(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc)
    assert "/command" in str(exc)


def test_define_two_default_handlers(collector: HandlerCollector) -> None:
    # - Arrange -
    @collector.default
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.default
        async def handler_2(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc)
    assert "Default" in str(exc)


def test_define_two_chat_created_handlers(collector: HandlerCollector) -> None:
    # - Arrange -
    @collector.chat_created
    async def handler_1(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.chat_created
        async def handler_2(message: ChatCreatedEvent, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc)
    assert "Event" in str(exc)


def test_merge_collectors_with_same_command_handlers(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.handler(command="/command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.handler(command="/command")
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc)
    assert "/command" in str(exc)


def test_merge_collectors_with_default_handlers(collector: HandlerCollector) -> None:
    # - Arrange -
    @collector.default
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.default
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc)
    assert "Default" in str(exc)


def test_merge_collectors_with_chat_created_handlers(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.chat_created
    async def handler_1(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.chat_created
    async def handler_2(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc)
    assert "event" in str(exc)
