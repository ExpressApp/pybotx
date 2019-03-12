import pytest
from botx import Bot, Dispatcher
from gevent import Greenlet
from gevent.queue import Queue


class TestBot:
    def test_bot_init(self):
        with pytest.raises(ValueError):
            Bot()
        with pytest.raises(ValueError):
            Bot(bot_id="bot_token")
        with pytest.raises(ValueError):
            Bot(bot_host="example.host.com")
        with pytest.raises(ValueError):
            Bot(bot_id=1, bot_host="example.host.com")
        with pytest.raises(ValueError):
            Bot(bot_id="bot_token", bot_host=1)

    def test_bot_init_with_parameters(self):
        bot = Bot("bot_token", "example.host.com")
        assert bot.bot_id == "bot_token"
        assert bot.bot_host == "example.host.com"
        assert (
            bot.url_command == "https://example.host.com/api/v2/botx/command/callback"
        )
        assert (
            bot.url_notification
            == "https://example.host.com/api/v2/botx/notification/callback"
        )
        assert bot.url_file == "https://example.host.com/api/v1/botx/file/callback"
        assert isinstance(bot._dispatcher, Dispatcher)
        assert bot._dispatcher._bot == bot
        assert isinstance(bot._dispatcher._jobs_queue, Queue)
        assert isinstance(bot._dispatcher._workers, list)

    def test_bot_start_webhook(self):
        bot = Bot("bot_token", "example.host.com")
        with pytest.raises(ValueError):
            bot.start_bot(workers_number="4")
        bot.start_bot(workers_number=4)
        assert len(bot._dispatcher._workers) == 4
        for worker in bot._dispatcher._workers:
            assert isinstance(worker, Greenlet)
