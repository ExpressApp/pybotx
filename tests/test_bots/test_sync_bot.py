import json
import pathlib
import uuid

import pytest
import requests
import responses

from botx import CTS, Bot, File, Message, ReplyMessage
from botx.core import TEXT_MAX_LENGTH, BotXAPI, BotXException
from botx.models import ResponseCommand, ResponseNotification, ResponseResult


class TestSyncBot:
    def test_commands_execution(self, message_data, bot_with_token):
        bot = bot_with_token
        bot.start()

        testing_array = []

        @bot.handler
        def handler(*_):
            testing_array.append(1)

        bot.execute_command(message_data(command="/handler"))

        bot.stop()

        assert testing_array

    def test_raising_exception_when_message_is_too_big(
        self, valid_sync_requests_mock, message_data
    ):
        bot = Bot(workers=1)
        bot.start()

        text = "a" * (TEXT_MAX_LENGTH + 5)
        with pytest.raises(BotXException):
            bot.answer_message(text, Message(**message_data()))

        bot.stop()

    def test_raising_exception_when_accessing_unregistered_cts(self, message_data):
        bot = Bot(workers=1)
        bot.start()

        with pytest.raises(BotXException):
            bot.answer_message("", Message(**message_data()))

        bot.stop()

    class TestSyncBotCallsToAPI:
        def test_sending_message_with_file(self, message_data, bot_with_token):
            bot = bot_with_token
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def command_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V4.command.method,
                    BotXAPI.V4.command.url.format(host=message.host),
                    content_type="application/json",
                    callback=command_callback,
                )

                path = pathlib.Path(__file__).parents[1]
                with open(path / "files" / "file.json", "r") as f:
                    file = File.from_file(f)

                bot.answer_message("", message, file=file.file)

                request_data = testing_array[0]
                assert ResponseCommand(**request_data) == ResponseCommand(
                    bot_id=message.bot_id,
                    sync_id=message.sync_id,
                    command_result=ResponseResult(body=""),
                    file=file,
                )

            bot.stop()

        def test_sending_message_to_group_chat(self, message_data, bot_with_token):
            bot = bot_with_token
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def notification_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V4.notification.method,
                    BotXAPI.V4.notification.url.format(host=message.host),
                    content_type="application/json",
                    callback=notification_callback,
                )

                bot.send_message(
                    "", message.group_chat_id, message.bot_id, message.host
                )

                request_data = testing_array[0]
                assert ResponseNotification(**request_data) == ResponseNotification(
                    bot_id=message.bot_id,
                    group_chat_ids=[message.group_chat_id],
                    notification=ResponseResult(body=""),
                )

            bot.stop()

        def test_sending_message_to_many_group_chats(
            self, message_data, bot_with_token
        ):
            bot = bot_with_token
            bot.start()
            message = Message(**message_data())
            chats = [uuid.uuid4() for _ in range(4)]

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def notification_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V4.notification.method,
                    BotXAPI.V4.notification.url.format(host=message.host),
                    content_type="application/json",
                    callback=notification_callback,
                )

                bot.send_message("", chats, message.bot_id, message.host)

                request_data = testing_array[0]
                assert ResponseNotification(**request_data) == ResponseNotification(
                    bot_id=message.bot_id,
                    group_chat_ids=chats,
                    notification=ResponseResult(body=""),
                )

            bot.stop()

        def test_reply_with_token(
            self, message_data, host, secret, valid_sync_requests_mock
        ):
            bot = Bot(workers=1)
            bot.start()

            bot.add_cts(CTS(host=host, secret_key=secret))

            bot.reply(ReplyMessage.from_message("", Message(**message_data())))

            bot.stop()

            assert bot.get_cts_by_host(host).credentials.token == "result"

        def test_obtaining_token_only_once(self, message_data, secret):
            bot = Bot(workers=1)
            bot.start()
            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key=secret))

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def command_callback(*_):
                    return 200, {}, ""

                def token_callback(*_):
                    testing_array.append(1)
                    return 200, {}, json.dumps({"result": "token"})

                mock.add_callback(
                    BotXAPI.V4.command.method,
                    BotXAPI.V4.command.url.format(host=message.host),
                    content_type="application/json",
                    callback=command_callback,
                )
                mock.add_callback(
                    BotXAPI.V4.token.method,
                    BotXAPI.V4.token.url.format(
                        host=message.host, bot_id=message.bot_id
                    ),
                    content_type="application/json",
                    callback=token_callback,
                )

                bot.send_message("", message.sync_id, message.bot_id, message.host)
                bot.send_message("", message.sync_id, message.bot_id, message.host)

                assert len(testing_array) == 1

            bot.stop()

        def test_sending_file(self, message_data, bot_with_token):
            bot = bot_with_token
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def file_callback(request: requests.PreparedRequest):
                    testing_array.append(request.body)
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V4.file.method,
                    BotXAPI.V4.file.url.format(host=message.host),
                    content_type="multipart/form-data",
                    callback=file_callback,
                )

                path = pathlib.Path(__file__).parents[1]
                with open(path / "files" / "file.json", "r") as f:
                    file = File.from_file(f)

                bot.send_file(file.file, message.sync_id, message.bot_id, message.host)

                request_data = testing_array[0]
                assert file.raw_data in request_data

            bot.stop()

    class TestSyncBotCallsToAPIErrorHandling:
        def test_command_sending(
            self, message_data, wrong_sync_requests_mock, bot_with_token
        ):
            bot = bot_with_token
            bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                bot.answer_message("", message)

            bot.stop()

            print(e.value)

            assert "sync_id" in e.value.data

        def test_message_sending_to_chats(
            self, message_data, wrong_sync_requests_mock, bot_with_token
        ):
            bot = bot_with_token
            bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                bot.send_message(
                    "", message.group_chat_id, message.bot_id, message.host
                )

            assert "chat_id" in e.value.data

            with pytest.raises(BotXException) as e:
                bot.send_message(
                    "", [uuid.uuid4(), uuid.uuid4()], message.bot_id, message.host
                )

            assert "chat_ids_list" in e.value.data

            bot.stop()

        def test_file_sending(
            self, wrong_sync_requests_mock, message_data, bot_with_token
        ):
            bot = bot_with_token
            bot.start()

            message = Message(**message_data())

            path = pathlib.Path(__file__).parents[1]
            with open(path / "files" / "file.json", "r") as f:
                file = File.from_file(f)

            with pytest.raises(BotXException):
                bot.send_file(file.file, message.sync_id, message.bot_id, message.host)

            bot.stop()

        def test_token_obtaining(self, wrong_sync_requests_mock, message_data):
            bot = Bot(workers=1)
            bot.start()

            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key="secret"))

            with pytest.raises(BotXException) as e:
                bot.answer_message("", message)

            assert bot.get_cts_by_host(message.host).credentials is None
            assert "token" in str(e.value)

            bot.stop()
