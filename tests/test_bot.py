# @TODO: In production, remove `pytest` from requirements.txt

import pytest

from gevent import Greenlet
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from botx import Bot, Dispatcher


class TestBot:

    def test_bot_init(self):
        with pytest.raises(ValueError):
            Bot()
        with pytest.raises(ValueError):
            Bot(bot_id='bot_token')
        with pytest.raises(ValueError):
            Bot(bot_host='example.host.com')
        with pytest.raises(ValueError):
            Bot(bot_id=1, bot_host='example.host.com')
        with pytest.raises(ValueError):
            Bot(bot_id='bot_token', bot_host=1)

    def test_bot_init_with_parameters(self):
        bot = Bot('bot_token', 'example.host.com')
        assert bot.bot_id == 'bot_token'
        assert bot.bot_host == 'example.host.com'
        assert bot.url_command == \
            'https://example.host.com/api/v2/botx/command/callback'
        assert bot.url_notification == \
            'https://example.host.com/api/v2/botx/notification/callback'
        assert bot.url_file == \
            'https://example.host.com/api/v1/botx/file/callback'
        assert isinstance(bot.dispatcher, Dispatcher)
        assert bot.dispatcher._bot == bot
        assert bot._server == None
        assert isinstance(bot._jobs_queue, Queue)
        assert isinstance(bot._workers, list)
        assert bot._workers == []

    def test_bot_start_webhook(self):
        bot = Bot('bot_token', 'example.host.com')
        with pytest.raises(ValueError):
            bot.start_webhook(workers_number='4')
        bot.start_webhook(workers_number=4)
        assert isinstance(bot._server, WSGIServer)

    def test_bot_start_webhook_with_existing(self):
        bot = Bot('bot_token', 'example.host.com')
        bot._server = 'not a server'
        bot.start_webhook()
        assert bot._server == 'not a server'



