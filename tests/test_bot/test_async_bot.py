import pytest

from botx import (
    CTS,
    AsyncBot,
    BotCredentials,
    BotXException,
    CTSCredentials,
    Message,
    Status,
    StatusResult,
)


@pytest.mark.asyncio
async def test_async_bot_init(hostname):
    bot = AsyncBot()
    await bot.start()

    assert bot._dispatcher is not None
    assert bot._credentials == BotCredentials()

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_status_parsing(
    custom_router, custom_async_handler, custom_default_async_handler
):
    custom_router.add_handler(custom_async_handler)
    custom_router.add_handler(custom_default_async_handler)

    bot = AsyncBot()
    await bot.start()

    bot.add_commands(custom_router)

    assert await bot.parse_status() == Status(
        result=StatusResult(commands=[custom_async_handler.to_status_command()])
    )

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_command_executing(
    command_with_text_and_file, custom_async_handler_with_sync_command_body
):
    bot = AsyncBot()
    await bot.start()

    bot.add_handler(custom_async_handler_with_sync_command_body)
    assert await bot.parse_command(command_with_text_and_file)

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_token_obtaining(hostname, bot_id, async_requests):
    bot = AsyncBot()
    await bot.start()

    with pytest.raises(BotXException):
        await bot._obtain_token(hostname, bot_id)

    cts = CTS(host=hostname, secret_key="secret")
    bot.register_cts(cts)
    await bot._obtain_token(hostname, bot_id)
    assert bot._credentials.known_cts[cts.host] == (
        cts,
        CTSCredentials(bot_id=bot_id, result="token_for_operations"),
    )

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_token_obtaining_with_errored_request(
    hostname, bot_id, async_error_requests
):
    bot = AsyncBot()
    await bot.start()

    cts = CTS(host=hostname, secret_key="secret")
    bot.register_cts(cts)

    await bot._obtain_token(hostname, bot_id)
    assert bot._credentials.known_cts[cts.host][1] is None

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_message_as_command_sending(
    hostname, bot_id, async_requests, command_with_text_and_file
):
    command_array = []
    notification_array = []

    async def custom_command_sending(
        text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        command_array.append(
            (text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard)
        )

    async def custom_notification_sending(
        text, group_chat_ids, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        notification_array.append(
            (
                text,
                group_chat_ids,
                bot_id,
                host,
                file,
                recipients,
                mentions,
                bubble,
                keyboard,
            )
        )

    bot = AsyncBot()
    await bot.start()

    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    bot._send_command_result = custom_command_sending
    bot._send_notification_result = custom_notification_sending

    m = Message(**command_with_text_and_file)

    await bot.send_message(m.body, m.sync_id, m.bot_id, m.host, file=m.file.file)

    assert len(command_array) == 1
    assert command_array[0] == (
        m.body,
        m.sync_id,
        m.bot_id,
        m.host,
        m.file,
        "all",
        [],
        [],
        [],
    )

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_message_as_notification_sending(
    hostname, bot_id, async_requests, command_with_text_and_file
):
    command_array = []
    notification_array = []

    async def custom_command_sending(
        text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        command_array.append(
            (text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard)
        )

    async def custom_notification_sending(
        text, group_chat_ids, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        notification_array.append(
            (
                text,
                group_chat_ids,
                bot_id,
                host,
                file,
                recipients,
                mentions,
                bubble,
                keyboard,
            )
        )

    bot = AsyncBot()
    await bot.start()

    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    bot._send_command_result = custom_command_sending
    bot._send_notification_result = custom_notification_sending

    m = Message(**command_with_text_and_file)

    await bot.send_message(m.body, m.group_chat_id, m.bot_id, m.host, file=m.file.file)

    assert len(notification_array) == 1
    assert notification_array[0] == (
        m.body,
        [m.group_chat_id],
        m.bot_id,
        m.host,
        m.file,
        "all",
        [],
        [],
        [],
    )

    await bot.send_message(
        m.body,
        [m.group_chat_id, m.group_chat_id, m.group_chat_id],
        m.bot_id,
        m.host,
        file=m.file.file,
    )

    assert notification_array[1] == (
        m.body,
        [m.group_chat_id, m.group_chat_id, m.group_chat_id],
        m.bot_id,
        m.host,
        m.file,
        "all",
        [],
        [],
        [],
    )

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_requests(
    command_with_text_and_file, hostname, bot_id, async_requests
):
    bot = AsyncBot()
    await bot.start()

    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert (
        len(
            await bot._send_command_result(
                m.body, m.sync_id, m.bot_id, m.host, m.file, "all", [], [], []
            )
        )
        == 2
    )
    assert (
        len(
            await bot._send_notification_result(
                m.body, [m.group_chat_id], m.bot_id, m.host, m.file, "all", [], [], []
            )
        )
        == 2
    )
    assert len(await bot.send_file(m.file.file, m.sync_id, m.bot_id, m.host)) == 2

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_message_sending_error_requests(
    command_with_text_and_file, hostname, bot_id, async_error_requests
):
    bot = AsyncBot()
    await bot.start()

    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert (await bot.send_message(m.body, m.sync_id, m.bot_id, m.host)) != 200

    await bot.stop()


@pytest.mark.asyncio
async def test_async_bot_file_sending_error_requests(
    command_with_text_and_file, hostname, bot_id, async_error_requests
):
    bot = AsyncBot()
    await bot.start()

    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert (await bot.send_file(m.file.file, m.sync_id, m.bot_id, m.host)) != 200

    await bot.stop()


@pytest.mark.asyncio
async def test_sync_bot_work_with_disabled_credentials(
    async_requests, command_with_text_and_file
):
    bot = AsyncBot(disable_credentials=True)
    await bot.start()

    def token_obtaining_mock(**data):
        raise Exception()

    bot._obtain_token = token_obtaining_mock

    m = Message(**command_with_text_and_file)
    await bot.send_message(m.body, m.sync_id, m.bot_id, m.host)

    await bot.stop()


@pytest.mark.asyncio
async def test_async_dispatcher_throws_bot_to_command(command_with_text_and_file):
    bot = AsyncBot()

    await bot.start()

    @bot.command
    async def cmd(m, b):
        assert b == bot

    await bot.parse_command(command_with_text_and_file)
    await bot.stop()


@pytest.mark.asyncio
async def test_async_answer_message(command_with_text_and_file, async_requests):
    bot = AsyncBot(disable_credentials=True)
    await bot.start()

    message = Message(**command_with_text_and_file)
    await bot.answer_message(message.body, message)

    await bot.stop()
