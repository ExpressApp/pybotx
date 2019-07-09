import json
import pathlib
import re
import uuid

import aresponses
import pytest
import requests
import responses
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import json_response

from botx import (
    CTS,
    AsyncBot,
    Bot,
    BotCredentials,
    File,
    HandlersCollector,
    Message,
    ReplyMessage,
    Status,
    StatusResult,
    SystemEventsEnum,
)
from botx.core import TEXT_MAX_LENGTH, BotXAPI, BotXException
from botx.models import ResponseCommand, ResponseNotification, ResponseResult
from tests.utils import get_route_path_from_template


class TestBaseBot:
    def test_default_credentials_are_empty(self):
        bot = Bot(workers=1)

        assert bot.credentials == BotCredentials()

    def test_changing_urls_when_disabling_credentials(self, message_data):
        bot = Bot(workers=1, disable_credentials=True)
        bot.start()

        message = Message(**message_data())

        with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
            testing_array = []

            def command_callback(*_):
                testing_array.append("command")
                return 200, {}, ""

            def notification_callback(*_):
                testing_array.append("notification")
                return 200, {}, ""

            mock.add_callback(
                BotXAPI.V2.notification.method,
                BotXAPI.V2.notification.url.format(host=message.host),
                content_type="application/json",
                callback=notification_callback,
            )
            mock.add_callback(
                BotXAPI.V2.command.method,
                BotXAPI.V2.command.url.format(host=message.host),
                content_type="application/json",
                callback=command_callback,
            )

            bot.send_message("", message.sync_id, message.bot_id, message.host)
            bot.send_message("", message.group_chat_id, message.bot_id, message.host)

            assert testing_array == ["command", "notification"]

        bot.stop()

    def test_adding_cts(self, host, secret):
        cts = CTS(host=host, secret_key=secret)

        bot = Bot(workers=1)
        bot.add_cts(cts)

        assert bot.get_cts_by_host(host) == cts

    def test_raising_exception_for_retrieving_token_for_unregistered_cts(self, host):
        bot = Bot(workers=1)

        with pytest.raises(BotXException):
            bot.get_token_from_cts(host)

    def test_adding_credentials_without_duplicates(self, host, secret):
        bot = Bot(workers=1)
        credentials = BotCredentials(known_cts=[CTS(host=host, secret_key=secret)])

        bot.add_credentials(credentials)
        bot.add_credentials(credentials)

        assert bot.credentials == credentials

    def test_bot_append_self_to_handlers_args(self, handler_factory):
        bot = Bot(workers=1)
        collector = HandlersCollector()

        collector.handler(handler_factory("sync"), command="cmd")
        bot.include_handlers(collector)

        handler = bot.handlers[re.compile(re.escape("/cmd"))]
        assert handler.callback.args == (bot,)

    def test_status_property(self, handler_factory):
        bot = Bot(workers=1)
        bot.handler(handler_factory("sync"))

        assert bot.status == Status(
            result=StatusResult(
                commands=[
                    bot.handlers[
                        re.compile(re.escape("/sync-handler"))
                    ].to_status_command()
                ]
            )
        )

    def test_next_step_handlers_execution(self, message_data):
        bot = Bot(workers=1, disable_credentials=True)
        bot.start()

        message = Message(**message_data(command="/my-handler"))

        testing_array = []

        @bot.handler
        def my_handler(msg: Message, *_):
            def ns_handler(*args):
                testing_array.append(args)

            bot.register_next_step_handler(msg, ns_handler)

        bot.execute_command(message.dict())
        bot.execute_command(message.dict())

        bot.stop()

        assert testing_array == [(message, bot)]

    def test_raising_exception_for_registration_ns_handlers_without_users(
        self, message_data
    ):
        bot = Bot(workers=1, disable_credentials=True)
        bot.start()

        message = Message(**message_data(command=SystemEventsEnum.chat_created.value))
        message.user.user_huid = None

        testing_array = []

        @bot.system_event_handler(event=SystemEventsEnum.chat_created)
        def handler(msg: Message, *_):
            def ns_handler(*_):
                pass

            try:
                bot.register_next_step_handler(msg, ns_handler)
            except BotXException as e:
                testing_array.append(e)

        bot.execute_command(message.dict())

        bot.stop()

        assert testing_array


class TestSyncBot:
    def test_commands_execution(self, message_data):
        bot = Bot(workers=1)
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
        def test_sending_message_with_file(self, message_data):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def command_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V2.command.method,
                    BotXAPI.V2.command.url.format(host=message.host),
                    content_type="application/json",
                    callback=command_callback,
                )

                path = pathlib.Path(__file__).parent
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

        def test_sending_message_to_group_chat(self, message_data):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def notification_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V2.notification.method,
                    BotXAPI.V2.notification.url.format(host=message.host),
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

        def test_sending_message_to_many_group_chats(self, message_data):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()
            message = Message(**message_data())
            chats = [uuid.uuid4() for _ in range(4)]

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def notification_callback(request: requests.PreparedRequest):
                    testing_array.append(json.loads(request.body.decode()))
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V2.notification.method,
                    BotXAPI.V2.notification.url.format(host=message.host),
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

                def command_callback(request: requests.PreparedRequest):
                    return 200, {}, ""

                def token_callback(request: requests.PreparedRequest):
                    testing_array.append(1)
                    return 200, {}, json.dumps({"result": "token"})

                mock.add_callback(
                    BotXAPI.V3.command.method,
                    BotXAPI.V3.command.url.format(host=message.host),
                    content_type="application/json",
                    callback=command_callback,
                )
                mock.add_callback(
                    BotXAPI.V2.token.method,
                    BotXAPI.V2.token.url.format(
                        host=message.host, bot_id=message.bot_id
                    ),
                    content_type="application/json",
                    callback=token_callback,
                )

                bot.send_message("", message.sync_id, message.bot_id, message.host)
                bot.send_message("", message.sync_id, message.bot_id, message.host)

                assert len(testing_array) == 1

            bot.stop()

        def test_sending_file(self, message_data):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()
            message = Message(**message_data())

            with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
                testing_array = []

                def file_callback(request: requests.PreparedRequest):
                    testing_array.append(request.body)
                    return 200, {}, ""

                mock.add_callback(
                    BotXAPI.V1.file.method,
                    BotXAPI.V1.file.url.format(host=message.host),
                    content_type="multipart/form-data",
                    callback=file_callback,
                )

                path = pathlib.Path(__file__).parent
                with open(path / "files" / "file.json", "r") as f:
                    file = File.from_file(f)

                bot.send_file(file.file, message.sync_id, message.bot_id, message.host)

                request_data = testing_array[0]
                assert file.raw_data in request_data

            bot.stop()

    class TestSyncBotCallsToAPIErrorHandling:
        def test_command_sending(self, message_data, wrong_sync_requests_mock):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                bot.answer_message("", message)

            bot.stop()

            assert "sync_id" in e.value.data

        def test_message_sending_to_chats(self, message_data, wrong_sync_requests_mock):
            bot = Bot(workers=1, disable_credentials=True)
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

        def test_file_sending(self, wrong_sync_requests_mock, message_data):
            bot = Bot(workers=1, disable_credentials=True)
            bot.start()

            message = Message(**message_data())

            path = pathlib.Path(__file__).parent
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
        async def test_sending_message_with_file(self, message_data, host, bot_id):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def command_callback(request: BaseRequest):
                    testing_array.append(await request.json())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V2.command.url),
                    BotXAPI.V2.command.method.lower(),
                    command_callback,
                )

                path = pathlib.Path(__file__).parent
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
        async def test_sending_message_to_group_chat(self, message_data, host):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def notification_callback(request: BaseRequest):
                    testing_array.append(await request.json())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V2.notification.url),
                    BotXAPI.V2.notification.method.lower(),
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
        async def test_sending_message_to_many_group_chats(self, message_data, host):
            bot = AsyncBot(disable_credentials=True)
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
                    get_route_path_from_template(BotXAPI.V2.notification.url),
                    BotXAPI.V2.notification.method.lower(),
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
                        get_route_path_from_template(BotXAPI.V2.token.url).format(
                            bot_id=bot_id
                        ),
                        BotXAPI.V2.token.method.lower(),
                        token_callback,
                    )

                    mock.add(
                        host,
                        get_route_path_from_template(BotXAPI.V3.command.url),
                        BotXAPI.V3.command.method.lower(),
                        command_callback,
                    )

                    await bot.send_message(
                        "", message.sync_id, message.bot_id, message.host
                    )

            assert len(testing_array) == 1

            await bot.stop()

        @pytest.mark.asyncio
        async def test_sending_file(self, message_data, host):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()
            message = Message(**message_data())

            async with aresponses.ResponsesMockServer() as mock:
                testing_array = []

                async def file_callback(request: BaseRequest):
                    testing_array.append((await request.text()).encode())
                    return json_response()

                mock.add(
                    host,
                    get_route_path_from_template(BotXAPI.V1.file.url),
                    BotXAPI.V1.file.method.lower(),
                    file_callback,
                )

                path = pathlib.Path(__file__).parent
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
        async def test_command_sending(self, message_data, wrong_async_requests_mock):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.answer_message("", message)

            await bot.stop()

            assert "sync_id" in e.value.data

        @pytest.mark.asyncio
        async def test_message_sending_to_chat(
            self, message_data, wrong_async_requests_mock
        ):
            bot = AsyncBot(disable_credentials=True)
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
            self, message_data, wrong_async_requests_mock
        ):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()

            message = Message(**message_data())

            with pytest.raises(BotXException) as e:
                await bot.send_message(
                    "", [uuid.uuid4(), uuid.uuid4()], message.bot_id, message.host
                )

            assert "chat_ids_list" in e.value.data

            await bot.stop()

        @pytest.mark.asyncio
        async def test_file_sending(self, wrong_async_requests_mock, message_data):
            bot = AsyncBot(disable_credentials=True)
            await bot.start()

            message = Message(**message_data())

            path = pathlib.Path(__file__).parent
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
