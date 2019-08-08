import uuid

import pytest

from botx import CTS, Bot, BotXException, Message, ReplyMessage, SendingCredentials
from botx.core import TEXT_MAX_LENGTH
from botx.helpers import call_coroutine_as_function
from botx.models import (
    BotXCommandResultPayload,
    BotXNotificationPayload,
    BotXResultPayload,
)
from tests.utils import get_test_route


class TestAsyncBot:
    @pytest.mark.asyncio
    async def test_commands_execution(self, message_data):
        bot = Bot()
        await bot.start()

        testing_array = []

        @bot.handler
        async def handler(*_):
            testing_array.append(1)

        await bot.execute_command(message_data(command="/handler"))
        await bot.stop()

        assert testing_array

    @pytest.mark.asyncio
    async def test_raising_exception_when_message_is_too_big(
        self, message_data, get_bot
    ):
        bot = get_bot()

        text = "a" * (TEXT_MAX_LENGTH + 5)
        with pytest.raises(BotXException):
            await bot.answer_message(text, Message(**message_data()))

    @pytest.mark.asyncio
    async def test_raising_exception_when_accessing_unregistered_cts(
        self, message_data, get_bot
    ):
        bot = get_bot()

        with pytest.raises(BotXException):
            await bot.answer_message("", Message(**message_data()))

    @pytest.mark.asyncio
    async def test_raising_error_when_both_sync_id_and_chats_ids_missed(
        self, message_data, get_bot
    ):
        bot = get_bot(set_token=True)
        message = Message(**message_data())
        with pytest.raises(BotXException) as e:
            await bot.send_message(
                "", SendingCredentials(bot_id=message.bot_id, host=message.host)
            )

    @pytest.mark.asyncio
    async def test_set_chat_id_in_reply(self, message_data, get_bot):
        bot = get_bot(set_token=True)
        message = Message(**message_data())

        reply_msg = ReplyMessage.from_message("", message)
        reply_msg.sync_id = None
        reply_msg.chat_ids = [uuid.uuid4()]
        await bot.reply(reply_msg)

    @pytest.mark.asyncio
    async def test_set_many_chat_ids_in_reply(self, message_data, get_bot):
        bot = get_bot(set_token=True)
        message = Message(**message_data())

        reply_msg = ReplyMessage.from_message("", message)
        reply_msg.chat_ids = [uuid.uuid4()]
        await bot.reply(reply_msg)

    class TestAsyncBotCallsToAPI:
        @pytest.mark.asyncio
        async def test_sending_message_with_file(
            self, message_data, get_bot, json_file
        ):
            testing_array = []

            bot = get_bot(command_route=get_test_route(testing_array), set_token=True)
            await bot.start()
            message = Message(**message_data())

            await bot.answer_message("", message, file=json_file.file)

            request_data = testing_array[0]
            assert BotXCommandResultPayload(**request_data) == BotXCommandResultPayload(
                bot_id=message.bot_id,
                sync_id=message.sync_id,
                command_result=BotXResultPayload(body=""),
                file=json_file,
            )

            await bot.stop()

        @pytest.mark.asyncio
        async def test_sending_message_to_group_chat(self, message_data, get_bot):
            testing_array = []

            bot = get_bot(
                notification_route=get_test_route(testing_array), set_token=True
            )
            message = Message(**message_data())

            await bot.send_message(
                "",
                SendingCredentials(
                    chat_ids=[message.group_chat_id],
                    bot_id=message.bot_id,
                    host=message.host,
                ),
            )

            request_data = testing_array[0]
            assert BotXNotificationPayload(**request_data) == BotXNotificationPayload(
                bot_id=message.bot_id,
                group_chat_ids=[message.group_chat_id],
                notification=BotXResultPayload(body=""),
            )

        @pytest.mark.asyncio
        async def test_sending_message_to_many_group_chats(self, message_data, get_bot):
            testing_array = []

            bot = get_bot(
                notification_route=get_test_route(testing_array), set_token=True
            )
            message = Message(**message_data())
            chats = [uuid.uuid4() for _ in range(4)]

            await bot.send_message(
                "",
                SendingCredentials(
                    chat_ids=chats, bot_id=message.bot_id, host=message.host
                ),
            )

            request_data = testing_array[0]
            assert BotXNotificationPayload(**request_data) == BotXNotificationPayload(
                bot_id=message.bot_id,
                group_chat_ids=chats,
                notification=BotXResultPayload(body=""),
            )

        @pytest.mark.asyncio
        async def test_reply_with_token(self, message_data, host, secret, get_bot):
            bot = get_bot()
            bot.add_cts(CTS(host=host, secret_key=secret))

            await bot.reply(ReplyMessage.from_message("", Message(**message_data())))
            assert bot.get_cts_by_host(host).credentials.token == "result"

        @pytest.mark.asyncio
        async def test_obtaining_token_only_once(
            self, message_data, secret, host, bot_id, get_bot
        ):
            testing_array = []

            bot = get_bot(
                command_route=get_test_route(),
                token_route=get_test_route(testing_array),
            )
            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key=secret))

            await bot.send_message(
                "",
                SendingCredentials(
                    sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
                ),
            )

            assert len(testing_array) == 1

        @pytest.mark.asyncio
        async def test_sending_file(self, message_data, host, get_bot, json_file):
            testing_array = []

            bot = get_bot(file_route=get_test_route(testing_array), set_token=True)
            message = Message(**message_data())

            await bot.send_file(
                json_file.file,
                SendingCredentials(
                    sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
                ),
            )

            request_data = testing_array[0]
            assert json_file.raw_data in (await request_data["file"].read())

    class TestAsyncBotCallsToAPIErrorHandling:
        @pytest.mark.asyncio
        async def test_command_sending(self, message_data, get_bot):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.answer_message("", message)

            assert "sync_id" in str(e.value.data)

        @pytest.mark.asyncio
        async def test_message_sending_to_chat(self, message_data, get_bot):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.send_message(
                    "",
                    SendingCredentials(
                        chat_ids=[message.group_chat_id],
                        bot_id=message.bot_id,
                        host=message.host,
                    ),
                )

            assert "chat_ids" in str(e.value.data)

        @pytest.mark.asyncio
        async def test_file_sending(self, message_data, get_bot, json_file):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException):
                await bot.send_file(
                    json_file.file,
                    SendingCredentials(
                        sync_id=message.sync_id,
                        bot_id=message.bot_id,
                        host=message.host,
                    ),
                )

        @pytest.mark.asyncio
        async def test_token_obtaining(self, message_data, get_bot):
            bot = get_bot(generate_error_response=True)
            message = Message(**message_data())
            bot.add_cts(CTS(host=message.host, secret_key="secret"))

            with pytest.raises(BotXException) as e:
                await bot.answer_message("", message)

            assert bot.get_cts_by_host(message.host).credentials is None
            assert "token" in str(e.value)

    class TestSyncBotCallsToAPI:
        def test_sending_message_with_file(self, message_data, get_bot, json_file):
            testing_array = []

            bot = get_bot(command_route=get_test_route(testing_array), set_token=True)
            message = Message(**message_data())

            bot.answer_message("", message, file=json_file.file)

            request_data = testing_array[0]
            assert BotXCommandResultPayload(**request_data) == BotXCommandResultPayload(
                bot_id=message.bot_id,
                sync_id=message.sync_id,
                command_result=BotXResultPayload(body=""),
                file=json_file,
            )

        def test_sending_message_to_group_chat(self, message_data, get_bot):
            testing_array = []

            bot = get_bot(
                notification_route=get_test_route(testing_array), set_token=True
            )
            message = Message(**message_data())

            bot.send_message(
                "",
                SendingCredentials(
                    chat_ids=[message.group_chat_id],
                    bot_id=message.bot_id,
                    host=message.host,
                ),
            )

            request_data = testing_array[0]
            assert BotXNotificationPayload(**request_data) == BotXNotificationPayload(
                bot_id=message.bot_id,
                group_chat_ids=[message.group_chat_id],
                notification=BotXResultPayload(body=""),
            )

        def test_sending_message_to_many_group_chats(self, message_data, get_bot):
            testing_array = []

            bot = get_bot(
                notification_route=get_test_route(testing_array), set_token=True
            )
            message = Message(**message_data())
            chats = [uuid.uuid4() for _ in range(4)]

            bot.send_message(
                "",
                SendingCredentials(
                    chat_ids=chats, bot_id=message.bot_id, host=message.host
                ),
            )

            request_data = testing_array[0]
            assert BotXNotificationPayload(**request_data) == BotXNotificationPayload(
                bot_id=message.bot_id,
                group_chat_ids=chats,
                notification=BotXResultPayload(body=""),
            )

        def test_reply_with_token(self, message_data, host, secret, get_bot):
            bot = get_bot()
            bot.add_cts(CTS(host=host, secret_key=secret))

            bot.reply(ReplyMessage.from_message("", Message(**message_data())))
            assert bot.get_cts_by_host(host).credentials.token == "result"

        def test_obtaining_token_only_once(
            self, message_data, secret, host, bot_id, get_bot
        ):
            testing_array = []

            bot = get_bot(
                command_route=get_test_route(),
                token_route=get_test_route(testing_array),
            )
            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key=secret))

            bot.send_message(
                "",
                SendingCredentials(
                    sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
                ),
            )

            assert len(testing_array) == 1

        def test_sending_file(self, message_data, host, get_bot, json_file):
            testing_array = []

            bot = get_bot(file_route=get_test_route(testing_array), set_token=True)
            message = Message(**message_data())

            bot.send_file(
                json_file.file,
                SendingCredentials(
                    sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
                ),
            )

            request_data = testing_array[0]
            assert json_file.raw_data in (
                call_coroutine_as_function(request_data["file"].read)
            )

    class TestSyncBotCallsToAPIErrorHandling:
        def test_command_sending(self, message_data, get_bot):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                bot.answer_message("", message)

            assert "sync_id" in str(e.value.data)

        def test_message_sending_to_chat(self, message_data, get_bot):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                bot.send_message(
                    "",
                    SendingCredentials(
                        chat_ids=[message.group_chat_id],
                        bot_id=message.bot_id,
                        host=message.host,
                    ),
                )

            assert "chat_ids" in str(e.value.data)

        def test_file_sending(self, message_data, get_bot, json_file):
            bot = get_bot(set_token=True, generate_error_response=True)
            message = Message(**message_data())

            with pytest.raises(BotXException):
                bot.send_file(
                    json_file.file,
                    SendingCredentials(
                        sync_id=message.sync_id,
                        bot_id=message.bot_id,
                        host=message.host,
                    ),
                )

        def test_token_obtaining(self, message_data, get_bot):
            bot = get_bot(generate_error_response=True)
            message = Message(**message_data())
            bot.add_cts(CTS(host=message.host, secret_key="secret"))

            with pytest.raises(BotXException) as e:
                bot.answer_message("", message)

            assert bot.get_cts_by_host(message.host).credentials is None
            assert "token" in str(e.value)
