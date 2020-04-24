from typing import Optional

import pytest

from botx import (
    AsyncClient,
    Bot,
    Client,
    DependencyFailure,
    Depends,
    IncomingMessage,
    Message,
    TestClient,
)


class TestPassingSpecialDependencies:
    @pytest.mark.asyncio
    async def test_passing_message_as_dependency(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        msg: Optional[Message] = None
        bot.collector.default_message_handler = None

        @bot.default
        async def handler_with_message(message: Message) -> None:
            nonlocal msg
            msg = message

        await client.send_command(incoming_message)

        assert msg.incoming_message == incoming_message

    @pytest.mark.asyncio
    async def test_passing_bot_as_dependency(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        dep_bot: Optional[Bot] = None
        bot.collector.default_message_handler = None

        @bot.default
        async def handler_with_message(handler_bot: Bot) -> None:
            nonlocal dep_bot
            dep_bot = handler_bot

        await client.send_command(incoming_message)

        assert dep_bot == bot

    @pytest.mark.asyncio
    async def test_passing_async_client_as_dependency(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        bot_client: Optional[AsyncClient] = None
        bot.collector.default_message_handler = None

        @bot.default
        async def handler_with_message(botx_client: AsyncClient) -> None:
            nonlocal bot_client
            bot_client = botx_client

        await client.send_command(incoming_message)

        assert bot_client == bot.client

    @pytest.mark.asyncio
    async def test_passing_sync_client_as_dependency(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        bot_client: Optional[Client] = None
        bot.collector.default_message_handler = None

        @bot.default
        async def handler_with_message(botx_client: Client) -> None:
            nonlocal bot_client
            bot_client = botx_client

        await client.send_command(incoming_message)

        assert bot_client == bot.sync_client

    @pytest.mark.asyncio
    async def test_solving_forward_references_for_special_dependencies(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        bot_client: Optional[AsyncClient] = None
        bot.collector.default_message_handler = None

        @bot.default
        async def handler_with_message(botx_client: "AsyncClient") -> None:
            nonlocal bot_client
            bot_client = botx_client

        await client.send_command(incoming_message)

        assert bot_client == bot.client


def test_error_passing_non_special_param_or_dependency(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    with pytest.raises(ValueError):

        @bot.handler
        def handler(_: int) -> None:
            ...  # pragma: no cover


@pytest.mark.asyncio
async def test_dependency_executed_only_once_per_message(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    counter = 0
    bot.collector.default_message_handler = None

    def increase_counter() -> None:
        nonlocal counter
        counter += 1

    @bot.default(dependencies=[Depends(increase_counter)])
    async def handler_with_message(_: None = Depends(increase_counter)) -> None:
        ...

    await client.send_command(incoming_message)

    assert counter == 1

    await client.send_command(incoming_message)

    assert counter == 2


@pytest.mark.asyncio
async def test_that_dependency_can_be_overriden(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    incoming_message.command.body = "/command with arguments"

    entered_into_dependency = False

    def original_dependency() -> None:
        ...  # pragma: no cover

    async def fake_dependency() -> None:
        nonlocal entered_into_dependency
        entered_into_dependency = True

    @bot.handler(command="/command", dependencies=[Depends(original_dependency)])
    async def handler_for_command() -> None:
        ...  # pragma: no cover

    bot.dependency_overrides[original_dependency] = fake_dependency

    await client.send_command(incoming_message)

    assert entered_into_dependency


@pytest.mark.asyncio
async def test_that_flow_can_be_stopped_by_raising_dependency_error(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    bot.collector.default_message_handler = None
    entered_into_dependency = False
    entered_into_handler = False

    def first_success_dependency() -> None:
        ...

    async def second_failed_dependency() -> None:
        nonlocal entered_into_dependency
        entered_into_dependency = True
        raise DependencyFailure

    def third_dependency_that_wont_be_executed() -> None:
        ...  # pragma: no cover

    @bot.default(
        dependencies=[
            Depends(first_success_dependency),
            Depends(second_failed_dependency),
            Depends(third_dependency_that_wont_be_executed),
        ]
    )
    async def handler_for_command_that_wont_be_executed() -> None:  # pragma: no cover
        nonlocal entered_into_handler
        entered_into_handler = True

    await client.send_command(incoming_message)

    assert entered_into_dependency and not entered_into_handler
