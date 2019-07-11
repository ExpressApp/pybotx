import pathlib
import uuid

import aresponses
import pytest
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import json_response

from botx import CTS, AsyncBot, File, Message, ReplyMessage
from botx.core import TEXT_MAX_LENGTH, BotXAPI, BotXException
from botx.models import ResponseCommand, ResponseNotification, ResponseResult
from tests.utils import get_route_path_from_template


class TestAsyncBot:
    @pytest.mark.asyncio
    async def test_commands_execution(self, message_data):
        bot = AsyncBot()
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
        self, valid_async_requests_mock, message_data
    ):
        bot = AsyncBot()
        await bot.start()

        text = "a" * (TEXT_MAX_LENGTH + 5)
        with pytest.raises(BotXException):
            await bot.answer_message(text, Message(**message_data()))

        await bot.stop()

    @pytest.mark.asyncio
    async def test_raising_exception_when_accessing_unregistered_cts(
        self, message_data
    ):
        bot = AsyncBot()
        await bot.start()

        with pytest.raises(BotXException):
            await bot.answer_message("", Message(**message_data()))

        await bot.stop()

    class TestAsyncBotCallsToAPI:
        @pytest.mark.asyncio
        async def test_sending_message_with_file(
            self, message_data, host, bot_id, async_bot_with_token: AsyncBot
        ):
            bot = async_bot_with_token
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def command_callback(request: BaseRequest):
                    testing_array.append(await request.json())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V4.command.url),
                    BotXAPI.V4.command.method.lower(),
                    command_callback,
                )

                path = pathlib.Path(__file__).parents[1]
                with open(path / "files" / "file.json", "r") as f:
                    file = File.from_file(f)

                await bot.answer_message("", message, file=file.file)

                request_data = testing_array[0]
                assert ResponseCommand(**request_data) == ResponseCommand(
                    bot_id=message.bot_id,
                    sync_id=message.sync_id,
                    command_result=ResponseResult(body=""),
                    file=file,
                )

            await bot.stop()

        @pytest.mark.asyncio
        async def test_sending_message_to_group_chat(
            self, message_data, host, async_bot_with_token: AsyncBot
        ):
            bot = async_bot_with_token
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def notification_callback(request: BaseRequest):
                    testing_array.append(await request.json())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V4.notification.url),
                    BotXAPI.V4.notification.method.lower(),
                    notification_callback,
                )

                await bot.send_message(
                    "", message.group_chat_id, message.bot_id, message.host
                )

                request_data = testing_array[0]
                assert ResponseNotification(**request_data) == ResponseNotification(
                    bot_id=message.bot_id,
                    group_chat_ids=[message.group_chat_id],
                    notification=ResponseResult(body=""),
                )

            await bot.stop()

        @pytest.mark.asyncio
        async def test_sending_message_to_many_group_chats(
            self, message_data, host, async_bot_with_token: AsyncBot
        ):
            bot = async_bot_with_token
            await bot.start()
            message = Message(**message_data())
            chats = [uuid.uuid4() for _ in range(4)]

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def notification_callback(request: BaseRequest):
                    testing_array.append(await request.json())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V4.notification.url),
                    BotXAPI.V4.notification.method.lower(),
                    notification_callback,
                )

                await bot.send_message("", chats, message.bot_id, message.host)

                request_data = testing_array[0]
                assert ResponseNotification(**request_data) == ResponseNotification(
                    bot_id=message.bot_id,
                    group_chat_ids=chats,
                    notification=ResponseResult(body=""),
                )

            await bot.stop()

        @pytest.mark.asyncio
        async def test_reply_with_token(
            self, message_data, host, secret, valid_async_requests_mock
        ):
            bot = AsyncBot()
            await bot.start()

            bot.add_cts(CTS(host=host, secret_key=secret))

            await bot.reply(ReplyMessage.from_message("", Message(**message_data())))

            await bot.stop()

            assert bot.get_cts_by_host(host).credentials.token == "result"

        @pytest.mark.asyncio
        async def test_obtaining_token_only_once(
            self, message_data, secret, host, bot_id
        ):
            bot = AsyncBot()
            await bot.start()
            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key=secret))

            testing_array = []

            async with aresponses.ResponsesMockServer() as mock:
                for i in range(2):

                    async def token_callback(*_):
                        testing_array.append(1)
                        return json_response({"result": "token"})

                    async def command_callback(*_):
                        return json_response()

                    mock.add(
                        host,
                        get_route_path_from_template(BotXAPI.V4.token.url).format(
                            bot_id=bot_id
                        ),
                        BotXAPI.V4.token.method.lower(),
                        token_callback,
                    )

                    mock.add(
                        host,
                        get_route_path_from_template(BotXAPI.V4.command.url),
                        BotXAPI.V4.command.method.lower(),
                        command_callback,
                    )

                    await bot.send_message(
                        "", message.sync_id, message.bot_id, message.host
                    )

            assert len(testing_array) == 1

            await bot.stop()

        @pytest.mark.asyncio
        async def test_sending_file(
            self, message_data, host, async_bot_with_token: AsyncBot
        ):
            bot = async_bot_with_token
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def file_callback(request: BaseRequest):
                    testing_array.append((await request.text()).encode())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V4.file.url),
                    BotXAPI.V4.file.method.lower(),
                    file_callback,
                )

                path = pathlib.Path(__file__).parents[1]
                with open(path / "files" / "file.json", "r") as f:
                    file = File.from_file(f)

                await bot.send_file(
                    file.file, message.sync_id, message.bot_id, message.host
                )

                request_data = testing_array[0]
                assert file.raw_data in request_data

            await bot.stop()

    class TestAsyncBotCallsToAPIErrorHandling:
        @pytest.mark.asyncio
        async def test_command_sending(
            self,
            message_data,
            wrong_async_requests_mock,
            async_bot_with_token: AsyncBot,
        ):
            bot = async_bot_with_token
            await bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.answer_message("", message)

            await bot.stop()

            assert "sync_id" in e.value.data

        @pytest.mark.asyncio
        async def test_message_sending_to_chat(
            self,
            message_data,
            wrong_async_requests_mock,
            async_bot_with_token: AsyncBot,
        ):
            bot = async_bot_with_token
            await bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.send_message(
                    "", message.group_chat_id, message.bot_id, message.host
                )

            assert "chat_id" in e.value.data

            await bot.stop()

        @pytest.mark.asyncio
        async def test_message_sending_to_many_chats(
            self,
            message_data,
            wrong_async_requests_mock,
            async_bot_with_token: AsyncBot,
        ):
            bot = async_bot_with_token
            await bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.send_message(
                    "", [uuid.uuid4(), uuid.uuid4()], message.bot_id, message.host
                )

            assert "chat_ids_list" in e.value.data

            await bot.stop()

        @pytest.mark.asyncio
        async def test_file_sending(
            self,
            wrong_async_requests_mock,
            message_data,
            async_bot_with_token: AsyncBot,
        ):
            bot = async_bot_with_token
            await bot.start()

            message = Message(**message_data())

            path = pathlib.Path(__file__).parents[1]
            with open(path / "files" / "file.json", "r") as f:
                file = File.from_file(f)

            with pytest.raises(BotXException):
                await bot.send_file(
                    file.file, message.sync_id, message.bot_id, message.host
                )

            await bot.stop()

        @pytest.mark.asyncio
        async def test_token_obtaining(self, wrong_async_requests_mock, message_data):
            bot = AsyncBot()
            await bot.start()

            message = Message(**message_data())

            bot.add_cts(CTS(host=message.host, secret_key="secret"))

            with pytest.raises(BotXException) as e:
                await bot.answer_message("", message)

            assert bot.get_cts_by_host(message.host).credentials is None
            assert "token" in str(e.value)

            await bot.stop()
