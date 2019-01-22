import sys
import json
import signal

import gevent.monkey
gevent.monkey.patch_all()

import requests
import gevent.signal

from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from botx.types.job import Job
from botx.types.message import Message
from botx.core.dispatcher import Dispatcher


class Bot:

    def __init__(self, token=None, base_url=None):
        """
        :param token: bot_id (uuid) - an unique identifier in BotX system
         :type token: str
        :param base_url: url
         :type base_url: str
        """

        if not token or not base_url:
            raise ValueError('`token` and `base_url` must be provided')

        self.token = token
        self.base_url = base_url
        self.url_command = '{}/api/v2/botx/command/callback'
        self.url_notification = '{}/api/v2/botx/notification/callback'
        self.url_file = '{}/api/v1/botx/file/callback'
        self.dispatcher = Dispatcher(bot=self)

        self._server = None
        self._jobs_queue = Queue()
        self._workers = []

    def start_webhook(self, address='127.0.0.1', port=5000, certfile=None,
                      keyfile=None):
        """
        :param address: A serving address
         :type address: str
        :param port: A serving port
         :type port: int
        :param certfile: A path to certificate file
         :type certfile: str
        :param keyfile: A path to key file
         :type keyfile: str
        """
        if not self._server:
            gevent.signal(signal.SIGINT, self.stop_webhook)
            self._start_webhook(address, port, certfile, keyfile)
            self._add_workers()
            self._invoke_workers()

    def _start_webhook(self, address, port, certfile, keyfile):
        if certfile and keyfile:
            server = WSGIServer((address, port), self._webhook_handle,
                                certfile=certfile, keyfile=keyfile)
        else:
            server = WSGIServer((address, port), self._webhook_handle)
        self._server = server
        self._server.start()

    def stop_webhook(self):
        # @TODO: kill all greenlets (self._kill_workers)
        self._server.stop()
        self._server = None
        sys.exit(signal.SIGINT)

    def _webhook_handle(self, env, start_response):
        headers = [('Content-Type', 'application/json')]
        response_ok = '200 OK'
        response_accepted = '202 Accepted'

        job = self.dispatcher.parse_request(env)
        if job and isinstance(job, Job) and isinstance(job.message, Message):
            self._jobs_queue.put_nowait(job)
            start_response(response_accepted, headers)
            return [json.dumps({"status": "accepted"}).encode('utf-8')]
        else:
            # @TODO: send a status
            pass

        start_response(response_ok, headers)
        return [json.dumps({"status": "ok"}).encode('utf-8')]

    def _add_workers(self, workers_number=4):
        self._workers = []
        for _ in range(workers_number):
            self._workers.append(gevent.spawn(self._process_request_worker))

    def _invoke_workers(self):
        gevent.joinall(self._workers)

    def _kill_workers(self):
        pass

    def _process_request_worker(self):
        while True:
            job = None
            try:
                job = self._jobs_queue.get_nowait()
            except gevent.queue.Empty:
                pass
            if job and isinstance(job, Job):
                job.command.func(job.message)
            gevent.sleep(0)

    def send_message(self, sync_id, chat_id, text):
        # sync_id or chat_id, both are paths where to send a message
        if not sync_id or not chat_id:
            raise ValueError()
