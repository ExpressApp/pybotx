import uuid

import pytest

from botx import (
    Bot,
    BubbleElement,
    File,
    IncomingMessage,
    KeyboardElement,
    Message,
    SendingCredentials,
    SendingMessage,
    ServerUnknownError,
    TestClient,
    UpdatePayload,
)


@pytest.mark.asyncio
async def test_returning_bot_commands_status(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    status = await bot.status()
    commands = [command.body for command in status.result.commands]
    assert commands == [
        "/regular-handler",
        "/handler-command",
        "/handler-command1",
        "/handler-command2",
        "/handler-command3",
        "/handler-command4",
        "/handler-command5",
        "/regular-handler-with-name",
        "/regular-handler-with-background-dependencies",
        "/regular-handler-that-included-in-status-by-callable-function",
    ]


@pytest.mark.asyncio
async def test_unknown_error_if_server_for_incoming_message_is_not_registered(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    incoming_message.user.host = "wrong.server.com"
    with pytest.raises(ServerUnknownError):
        await client.send_command(incoming_message)


class TestSendingMessageUsingSendMessage:
    @pytest.mark.asyncio
    async def test_sending_command_result_using_send_message(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        await bot.send_message(
            "some text",
            SendingCredentials(
                sync_id=incoming_message.sync_id,
                bot_id=incoming_message.bot_id,
                host=incoming_message.user.host,
            ),
            file=File.from_string("some content", "file.txt").file,
        )

        message = client.command_results[0]
        assert message.result.body == "some text"
        assert message.file == File.from_string("some content", "file.txt")

    @pytest.mark.asyncio
    async def test_sending_command_result_using_send_message_without_file(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        await bot.send_message(
            "some text",
            SendingCredentials(
                sync_id=incoming_message.sync_id,
                bot_id=incoming_message.bot_id,
                host=incoming_message.user.host,
            ),
        )

        message = client.command_results[0]
        assert message.result.body == "some text"
        assert not message.file

    @pytest.mark.asyncio
    async def test_sending_notification_using_send_message(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        await bot.send_message(
            "some text",
            SendingCredentials(
                chat_id=incoming_message.user.group_chat_id,
                bot_id=incoming_message.bot_id,
                host=incoming_message.user.host,
            ),
            file=File.from_string("some content", "file.txt").file,
        )

        message = client.notifications[0]
        assert message.result.body == "some text"
        assert message.file == File.from_string("some content", "file.txt")


class TestSendingMessageUsingSend:
    @pytest.mark.asyncio
    async def test_sending_command_result_using_send(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = SendingMessage.from_message(
            text="some text",
            file=File.from_string("some content", "file.txt"),
            message=Message.from_dict(incoming_message.dict(), bot),
        )
        message.add_keyboard_button(command="/cmd")
        message.add_bubble(command="/cmd")

        await bot.send(message)

        message = client.command_results[0]
        assert message.result.body == "some text"
        assert message.file == File.from_string("some content", "file.txt")
        assert message.result.bubble == [[BubbleElement(command="/cmd", label="/cmd")]]
        assert message.result.keyboard == [
            [KeyboardElement(command="/cmd", label="/cmd")]
        ]

    @pytest.mark.asyncio
    async def test_sending_notification_using_send(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = SendingMessage.from_message(
            text="some text",
            file=File.from_string("some content", "file.txt"),
            message=Message.from_dict(incoming_message.dict(), bot),
        )
        message.sync_id = None
        message.add_keyboard_button(command="/cmd")
        message.add_bubble(command="/cmd")

        await bot.send(message)

        message = client.notifications[0]
        assert message.result.body == "some text"
        assert message.file == File.from_string("some content", "file.txt")
        assert message.result.bubble == [[BubbleElement(command="/cmd", label="/cmd")]]
        assert message.result.keyboard == [
            [KeyboardElement(command="/cmd", label="/cmd")]
        ]


class TestSendingMessageUsingAnswerMessage:
    @pytest.mark.asyncio
    async def test_sending_command_result_using_answer_message_without_file(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        await bot.answer_message(
            "some text", Message.from_dict(incoming_message.dict(), bot)
        )

        message = client.command_results[0]
        assert message.result.body == "some text"

    @pytest.mark.asyncio
    async def test_sending_command_result_using_answer_message_with_file(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        await bot.answer_message(
            "some text",
            Message.from_dict(incoming_message.dict(), bot),
            file=File.from_string("some content", "file.txt"),
        )

        message = client.command_results[0]
        assert message.result.body == "some text"
        assert message.file == File.from_string("some content", "file.txt")


@pytest.mark.asyncio
async def test_returning_uuid_from_notification_sending(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    message = SendingMessage(
        text="text",
        chat_id=incoming_message.user.group_chat_id,
        bot_id=incoming_message.bot_id,
        host=incoming_message.user.host,
    )
    assert await bot.send(message)


@pytest.mark.asyncio
async def test_uuid_from_notification_sending_is_message_id(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    message_id = uuid.uuid4()
    message = SendingMessage(
        text="text",
        chat_id=incoming_message.user.group_chat_id,
        bot_id=incoming_message.bot_id,
        host=incoming_message.user.host,
        message_id=message_id,
    )
    notification_id = await bot.send(message)
    assert notification_id == message_id


class TestSendingFileUsingSendFile:
    @pytest.mark.asyncio
    async def test_sending_file_through_command_result(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)
        file = File.from_string("some content", "file.txt")

        await bot.send_file(file, message.credentials)

        message = client.command_results[0]
        assert message.file == file

    @pytest.mark.asyncio
    async def test_sending_file_through_notification(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)
        creds = message.credentials
        creds.sync_id = None
        file = File.from_string("some content", "file.txt")

        await bot.send_file(file, creds)

        message = client.notifications[0]
        assert message.file == file


@pytest.mark.asyncio
async def test_exception_when_sending_message_to_unknown_host(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    incoming_message.user.host = "error.com"

    with pytest.raises(ServerUnknownError):
        await bot.answer_message(
            "some text",
            Message.from_dict(incoming_message.dict(), bot),
            file=File.from_string("some content", "file.txt"),
        )


@pytest.mark.asyncio
async def test_updating_message(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    sync_id = await bot.answer_message(
        "some text",
        Message.from_dict(incoming_message.dict(), bot),
        file=File.from_string("some content", "file.txt"),
    )

    await bot.update_message(
        SendingCredentials(
            sync_id=sync_id,
            host=incoming_message.user.host,
            bot_id=incoming_message.bot_id,
        ),
        UpdatePayload(text="new text"),
    )

    update = client.message_updates[0].result
    assert update.body == "new text"


@pytest.mark.asyncio
class TestStealthMode:
    async def test_enable_stealth_mode(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)

        sync_id = await bot.answer_message("some text", message,)
        await bot.stealth_enable(
            SendingCredentials(
                sync_id=sync_id,
                host=incoming_message.user.host,
                bot_id=incoming_message.bot_id,
            ),
            chat_id=message.group_chat_id,
            burn_in=60,
            expire_in=60,
            disable_web=False,
        )
        msg = client.requests[-1]
        assert msg.group_chat_id == message.group_chat_id
        assert msg.burn_in == 60
        assert msg.expire_in == 60

    async def test_disable_stealth_mode(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)

        sync_id = await bot.answer_message("some text", message,)
        await bot.stealth_disable(
            SendingCredentials(
                sync_id=sync_id,
                host=incoming_message.user.host,
                bot_id=incoming_message.bot_id,
            ),
            chat_id=message.group_chat_id,
        )
        msg = client.requests[-1]
        assert msg.group_chat_id == message.group_chat_id


@pytest.mark.asyncio
class TestAddRemoveUsers:
    users_huids = list(uuid.uuid4() for _ in range(3))

    async def test_add_user(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)

        sync_id = await bot.answer_message("some text", message)
        await bot.add_users(
            SendingCredentials(
                sync_id=sync_id,
                host=incoming_message.user.host,
                bot_id=incoming_message.bot_id,
            ),
            chat_id=message.group_chat_id,
            users_huids=self.users_huids,
        )
        msg = client.requests[-1]
        assert msg.group_chat_id == message.group_chat_id
        assert msg.user_huids == self.users_huids

    async def test_remove_user(
        self, bot: Bot, incoming_message: IncomingMessage, client: TestClient
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)

        sync_id = await bot.answer_message("some text", message)
        await bot.remove_users(
            SendingCredentials(
                sync_id=sync_id,
                host=incoming_message.user.host,
                bot_id=incoming_message.bot_id,
            ),
            chat_id=message.group_chat_id,
            users_huids=self.users_huids,
        )
        msg = client.requests[-1]
        assert msg.group_chat_id == message.group_chat_id
        assert msg.user_huids == self.users_huids


@pytest.mark.asyncio
async def test_no_error_when_stopping_bot_with_no_tasks(bot: Bot) -> None:
    await bot.shutdown()


@pytest.mark.asyncio
async def test_bot_iterates_over_sorted_handlers(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    visited_by_body_v2_handler = False

    @bot.handler(command="/body")
    async def body_handler() -> None:
        ...  # pragma: no cover

    @bot.handler(command="/body-v2")
    async def body_v2_handler() -> None:
        nonlocal visited_by_body_v2_handler
        visited_by_body_v2_handler = True

    incoming_message.command.body = "/body-v2"
    await client.send_command(incoming_message)

    assert visited_by_body_v2_handler


@pytest.mark.asyncio
async def test_lifespan_events(bot: Bot) -> None:
    counter = 0

    async def lifespan_event(_bot: Bot) -> None:
        nonlocal counter
        counter += 1

    bot.startup_events = [lifespan_event]
    bot.shutdown_events = [lifespan_event]

    await bot.start()
    assert counter == 1

    await bot.shutdown()
    assert counter == 2