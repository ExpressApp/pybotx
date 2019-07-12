import asyncio

import pytest

from botx import (
    CTS,
    Bot,
    BotCredentials,
    HandlersCollector,
    Message,
    Status,
    StatusResult,
    SystemEventsEnum,
)
from botx.core import BotXException
from tests.utils import re_from_str


class TestBaseBot:
    def test_default_credentials_are_empty(self):
        bot = Bot()

        assert bot.credentials == BotCredentials()

    def test_adding_cts(self, host, secret):
        cts = CTS(host=host, secret_key=secret)

        bot = Bot()
        bot.add_cts(cts)

        assert bot.get_cts_by_host(host) == cts

    def test_adding_credentials_without_duplicates(self, host, secret):
        bot = Bot()
        credentials = BotCredentials(known_cts=[CTS(host=host, secret_key=secret)])

        bot.add_credentials(credentials)
        bot.add_credentials(credentials)

        assert bot.credentials == credentials

    def test_bot_append_self_to_handlers_args(self, handler_factory):
        bot = Bot()
        collector = HandlersCollector()

        collector.handler(handler_factory("sync"), command="cmd")
        bot.include_handlers(collector)

        handler = bot.handlers[re_from_str("/cmd")]
        assert handler.callback.args == (bot,)

    @pytest.mark.asyncio
    async def test_status(self, handler_factory):
        bot = Bot()
        bot.handler(handler_factory("sync"))

        assert await bot.status() == Status(
            result=StatusResult(
                commands=[
                    bot.handlers[re_from_str("/sync-handler")].to_status_command()
                ]
            )
        )

    @pytest.mark.asyncio
    async def test_next_step_handlers_execution(self, message_data):
        bot = Bot()
        await bot.start()

        message = Message(**message_data(command="/my-handler"))

        testing_array = []

        @bot.handler
        def my_handler(msg: Message, *_):
            def ns_handler(*args):
                testing_array.append(args)

            bot.register_next_step_handler(msg, ns_handler)

        await bot.execute_command(message.dict())

        await asyncio.sleep(0.1)

        await bot.execute_command(message.dict())

        await bot.stop()

        assert testing_array == [(message, bot)]

    @pytest.mark.asyncio
    async def test_raising_exception_for_registration_ns_handlers_without_users(
        self, message_data
    ):
        bot = Bot()
        await bot.start()

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

        await bot.execute_command(message.dict())

        await bot.stop()

        assert testing_array

    @pytest.mark.asyncio
    async def test_exception_catcher_handles_errors_from_handler(self, message_data):
        bot = Bot()
        await bot.start()

        message = Message(**message_data())

        testing_array = []

        re = RuntimeError("test")

        @bot.exception_catcher([Exception])
        async def error_handler(exc: Exception, msg: Message, bot: Bot) -> None:
            testing_array.append((exc, msg, bot))

        @bot.handler(command="cmd")
        async def handler(*_):
            raise re

        await bot.execute_command(message.dict())

        await bot.stop()

        assert testing_array[0] == (re, message, bot)

    @pytest.mark.asyncio
    async def test_exception_catcher_handles_errors_from_sync_handler(
        self, message_data
    ):
        bot = Bot()
        await bot.start()

        message = Message(**message_data())

        testing_array = []

        re = RuntimeError("test")

        @bot.exception_catcher([Exception])
        def error_handler(exc: Exception, msg: Message, bot: Bot) -> None:
            testing_array.append((exc, msg, bot))

        @bot.handler(command="cmd")
        def handler(*_):
            raise re

        await bot.execute_command(message.dict())

        await asyncio.sleep(0.1)

        await bot.stop()

        assert testing_array[0] == (re, message, bot)

    def test_raising_error_for_duplicate_exceptions_catchers(self):
        bot = Bot()

        @bot.exception_catcher([Exception])
        async def error_handler(*_) -> None:
            pass

        with pytest.raises(BotXException):

            @bot.exception_catcher([Exception])
            async def error_handler(*_) -> None:
                pass

    @pytest.mark.asyncio
    async def test_replacing_catcher_when_force_replace(self, message_data):
        bot = Bot()
        await bot.start()

        message = Message(**message_data())

        testing_array = []

        @bot.exception_catcher([Exception])
        async def error_handler(*_) -> None:
            testing_array.append(False)

        @bot.exception_catcher([Exception], force_replace=True)
        async def error_handler(*_) -> None:
            testing_array.append(True)

        @bot.handler(command="cmd")
        async def handler(*_):
            raise Exception

        await bot.execute_command(message.dict())

        await bot.stop()

        assert testing_array[0]
