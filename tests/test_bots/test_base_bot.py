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
        bot = Bot(workers=1)

        assert bot.credentials == BotCredentials()

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

        handler = bot.handlers[re_from_str("/cmd")]
        assert handler.callback.args == (bot,)

    def test_status_property(self, handler_factory):
        bot = Bot(workers=1)
        bot.handler(handler_factory("sync"))

        assert bot.status == Status(
            result=StatusResult(
                commands=[
                    bot.handlers[re_from_str("/sync-handler")].to_status_command()
                ]
            )
        )

    def test_next_step_handlers_execution(self, message_data):
        bot = Bot(workers=1)
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
        bot = Bot(workers=1)
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
