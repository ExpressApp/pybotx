import pytest
import requests
import responses

from botx import (
    CTS,
    Bot,
    BotCredentials,
    BotXException,
    CTSCredentials,
    Message,
    Status,
    StatusResult,
)


def test_responses():
    with responses.RequestsMock() as mock:
        mock.add(
            mock.GET,
            "https://some.domain.com/api/v1/action",
            json={"result": "success"},
        )

        assert requests.get("https://some.domain.com/api/v1/action?param=1").json() == {
            "result": "success"
        }


def test_sync_bot_init(hostname):
    bot = Bot()
    assert bot._dispatcher is not None
    assert bot._credentials == BotCredentials()


def test_sync_bot_start_and_shutdown():
    bot = Bot()
    bot.start()
    bot.stop()

    with pytest.raises(RuntimeError):
        bot._dispatcher._pool.submit(print, 1)


def test_sync_bot_status_parsing(custom_router, custom_handler, custom_default_handler):
    custom_router.add_handler(custom_handler)
    custom_router.add_handler(custom_default_handler)

    bot = Bot()
    bot.add_commands(custom_router)

    assert bot.parse_status() == Status(
        result=StatusResult(commands=[custom_handler.to_status_command()])
    )


def test_sync_bot_command_executing(command_with_text_and_file, custom_handler):
    bot = Bot()
    bot.add_handler(custom_handler)
    assert bot.parse_command(command_with_text_and_file)


def test_sync_bot_token_obtaining(hostname, bot_id, sync_requests):
    bot = Bot()

    with pytest.raises(BotXException):
        bot._obtain_token(hostname, bot_id)

    cts = CTS(host=hostname, secret_key="secret")

    bot.register_cts(cts)
    bot._obtain_token(hostname, bot_id)
    assert bot._credentials.known_cts[cts.host] == (
        cts,
        CTSCredentials(bot_id=bot_id, result="token_for_operations"),
    )


def test_sync_bot_token_obtaining_with_errored_request(
    hostname, bot_id, sync_error_requests
):
    bot = Bot()
    cts = CTS(host=hostname, secret_key="secret")
    bot.register_cts(cts)

    bot._obtain_token(hostname, bot_id)
    assert bot._credentials.known_cts[cts.host][1] is None


def test_sync_bot_message_as_command_sending(
    hostname, bot_id, command_with_text_and_file, sync_requests
):
    command_array = []
    notification_array = []

    def custom_command_sending(
        text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        command_array.append(
            (text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard)
        )

    def custom_notification_sending(
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

    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    bot._send_command_result = custom_command_sending
    bot._send_notification_result = custom_notification_sending

    m = Message(**command_with_text_and_file)

    bot.send_message(m.body, m.sync_id, m.bot_id, m.host, file=m.file.file)

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


def test_sync_bot_message_as_notification_sending(
    hostname, bot_id, command_with_text_and_file, sync_requests
):
    command_array = []
    notification_array = []

    def custom_command_sending(
        text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard
    ):
        command_array.append(
            (text, chat_id, bot_id, host, file, recipients, mentions, bubble, keyboard)
        )

    def custom_notification_sending(
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

    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    bot._send_command_result = custom_command_sending
    bot._send_notification_result = custom_notification_sending

    m = Message(**command_with_text_and_file)

    bot.send_message(m.body, m.group_chat_id, m.bot_id, m.host, file=m.file.file)

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

    bot.send_message(
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


def test_sync_bot_command_request(
    command_with_text_and_file, hostname, bot_id, sync_requests
):
    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert (
        len(
            bot._send_command_result(
                m.body, m.sync_id, m.bot_id, m.host, m.file, "all", [], [], []
            )
        )
        == 2
    )


def test_sync_bot_notification_request(
    command_with_text_and_file, hostname, bot_id, sync_requests
):
    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert (
        len(
            bot._send_notification_result(
                m.body, [m.group_chat_id], m.bot_id, m.host, m.file, "all", [], [], []
            )
        )
        == 2
    )


def test_sync_bot_file_request(
    command_with_text_and_file, hostname, bot_id, sync_requests
):
    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)

    assert len(bot.send_file(m.file.file, m.sync_id, m.bot_id, m.host)) == 2


def test_sync_bot_error_requests(
    command_with_text_and_file, hostname, bot_id, sync_error_requests
):
    bot = Bot()
    bot.register_cts(CTS(host=hostname, secret_key="secret"))

    m = Message(**command_with_text_and_file)
    assert bot.send_message(m.body, m.sync_id, m.bot_id, m.host) != 200
    assert bot.send_file(m.file.file, m.sync_id, m.bot_id, m.host)[1] != 200


def test_sync_bot_work_with_disabled_credentials(
    sync_requests, command_with_text_and_file
):
    bot = Bot(disable_credentials=True)

    def token_obtaining_mock(**data):
        raise Exception()

    bot._obtain_token = token_obtaining_mock

    m = Message(**command_with_text_and_file)
    bot.send_message(m.body, m.sync_id, m.bot_id, m.host)


def test_sync_dispatcher_throws_bot_to_command(command_with_text_and_file):
    bot = Bot()

    bot.start()

    @bot.command
    def cmd(m, b):
        assert b == bot

    bot.parse_command(command_with_text_and_file)
    bot.stop()


def test_sync_answer_message(command_with_text_and_file, sync_requests):
    bot = Bot(disable_credentials=True)
    bot.start()

    message = Message(**command_with_text_and_file)
    bot.answer_message(message.body, message)

    bot.stop()
