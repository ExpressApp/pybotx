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
    UpdatePayload,
    testing,
)


@pytest.mark.asyncio
async def test_returning_bot_commands_status(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    status = await bot.status()
    commands = [command.body for command in status.result.commands]
    assert commands == [
        "/regular-handler-that-included-in-status-by-callable-function",
        "/regular-handler-with-background-dependencies",
        "/regular-handler-with-name",
        "/handler-command1",
        "/handler-command2",
        "/handler-command4",
        "/handler-command5",
        "/handler-command3",
        "/regular-handler",
        "/handler-command",
        "/default-handler",
    ]


@pytest.mark.asyncio
async def test_unknown_error_if_server_for_incoming_message_is_not_registered(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    incoming_message.user.host = "wrong.server.com"
    with testing.TestClient(bot) as bot_client:
        with pytest.raises(ServerUnknownError):
            await bot_client.send_command(incoming_message)


class TestSendingMessageUsingSendMessage:
    @pytest.mark.asyncio
    async def test_sending_command_result_using_send_message(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        with testing.TestClient(bot) as client:
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
    async def test_sending_notification_using_send_message(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        with testing.TestClient(bot) as client:
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
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = SendingMessage.from_message(
            text="some text",
            file=File.from_string("some content", "file.txt"),
            message=Message.from_dict(incoming_message.dict(), bot),
        )
        message.add_keyboard_button(command="/cmd")
        message.add_bubble(command="/cmd")

        with testing.TestClient(bot) as client:
            await bot.send(message)

            message = client.command_results[0]
            assert message.result.body == "some text"
            assert message.file == File.from_string("some content", "file.txt")
            assert message.result.bubble == [
                [BubbleElement(command="/cmd", label="/cmd")]
            ]
            assert message.result.keyboard == [
                [KeyboardElement(command="/cmd", label="/cmd")]
            ]

    @pytest.mark.asyncio
    async def test_sending_notification_using_send(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = SendingMessage.from_message(
            text="some text",
            file=File.from_string("some content", "file.txt"),
            message=Message.from_dict(incoming_message.dict(), bot),
        )
        message.sync_id = None
        message.add_keyboard_button(command="/cmd")
        message.add_bubble(command="/cmd")

        with testing.TestClient(bot) as client:
            await bot.send(message)

            message = client.notifications[0]
            assert message.result.body == "some text"
            assert message.file == File.from_string("some content", "file.txt")
            assert message.result.bubble == [
                [BubbleElement(command="/cmd", label="/cmd")]
            ]
            assert message.result.keyboard == [
                [KeyboardElement(command="/cmd", label="/cmd")]
            ]

    @pytest.mark.asyncio
    async def test_error_when_sending_command_result_without_payload(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = SendingMessage.from_message(
            message=Message.from_dict(incoming_message.dict(), bot)
        )

        with testing.TestClient(bot):
            with pytest.raises(RuntimeError):
                await bot.send(message)

    @pytest.mark.asyncio
    async def test_error_when_sending_notification_without_payload(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = SendingMessage.from_message(
            message=Message.from_dict(incoming_message.dict(), bot)
        )
        message.sync_id = None

        with testing.TestClient(bot):
            with pytest.raises(RuntimeError):
                await bot.send(message)


class TestSendingMessageUsingAnswerMessage:
    @pytest.mark.asyncio
    async def test_sending_command_result_using_answer_message_without_file(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        with testing.TestClient(bot) as client:
            await bot.answer_message(
                "some text", Message.from_dict(incoming_message.dict(), bot)
            )

            message = client.command_results[0]
            assert message.result.body == "some text"

    @pytest.mark.asyncio
    async def test_sending_command_result_using_answer_message_with_file(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        with testing.TestClient(bot) as client:
            await bot.answer_message(
                "some text",
                Message.from_dict(incoming_message.dict(), bot),
                file=File.from_string("some content", "file.txt"),
            )

            message = client.command_results[0]
            assert message.result.body == "some text"
            assert message.file == File.from_string("some content", "file.txt")


class TestSendingFileUsingSendFile:
    @pytest.mark.asyncio
    async def test_sending_file_through_command_result(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)
        file = File.from_string("some content", "file.txt")
        with testing.TestClient(bot) as client:
            await bot.send_file(file, message.credentials)

            message = client.command_results[0]
            assert message.file == file

    @pytest.mark.asyncio
    async def test_sending_file_through_notification(
        self, bot: Bot, incoming_message: IncomingMessage
    ) -> None:
        message = Message.from_dict(incoming_message.dict(), bot)
        creds = message.credentials
        creds.sync_id = None
        file = File.from_string("some content", "file.txt")
        with testing.TestClient(bot) as client:
            await bot.send_file(file, creds)

            message = client.notifications[0]
            assert message.file == file


@pytest.mark.asyncio
async def test_accessing_token_only_once(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    async def fake_token_obtain(*_):
        raise RuntimeError  # pragma: no cover

    with testing.TestClient(bot) as client:
        await bot.answer_message(
            "some text",
            Message.from_dict(incoming_message.dict(), bot),
            file=File.from_string("some content", "file.txt"),
        )

        assert bot._get_cts_by_host(incoming_message.user.host).server_credentials.token

        bot.client.obtain_token = fake_token_obtain

        await bot.answer_message(
            "some text",
            Message.from_dict(incoming_message.dict(), bot),
            file=File.from_string("some content", "file.txt"),
        )

        assert len(client.messages) == 2


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
async def test_updating_message(bot: Bot, incoming_message: IncomingMessage) -> None:
    with testing.TestClient(bot) as client:
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

        update = client.message_updates[0]
        assert update.body == "new text"
