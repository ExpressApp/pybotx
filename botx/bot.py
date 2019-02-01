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
from botx.types.other import SyncID
from botx.types.status import Status
from botx.types.message import Message
from botx.types.response import ResponseCommand, ResponseCommandResult
from botx.core.dispatcher import Dispatcher


class Bot:

    def __init__(self, bot_id=None, bot_host=None):
        """
        :param bot_id: bot_id (uuid) - an unique identifier in BotX system
         :type bot_id: str
        :param bot_host: url (host) without type of connection
                         (e.g. `server.com`)
         :type bot_host: str
        """

        if not isinstance(bot_id, str) or not isinstance(bot_host, str):
            raise ValueError('`bot_id` and `bot_host` must be provided and '
                             'must be of str type')

        self.bot_id = bot_id
        self.bot_host = bot_host
        self.url_command = 'https://{}/api/v2/botx/command/callback'\
                           .format(self.bot_host)
        self.url_notification = 'https://{}/api/v2/botx/notification/callback'\
                                .format(self.bot_host)
        self.url_file = 'https://{}/api/v1/botx/file/callback'\
                        .format(self.bot_host)
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

    # @TODO: Add **kwargs for log='default' (or None) in WSGIServer object
    def _start_webhook(self, address, port, certfile, keyfile):
        if certfile and keyfile:
            server = WSGIServer((address, port), self._webhook_handle,
                                certfile=certfile, keyfile=keyfile)
        else:
            server = WSGIServer((address, port), self._webhook_handle)
        self._server = server
        self._server.start()

    def stop_webhook(self):
        # @TODO: kill all green lets (self._kill_workers)
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
        elif job and isinstance(job, Job) and isinstance(job.status, Status):
            start_response(response_ok, headers)
            return [json.dumps(job.status.to_dict()).encode('utf-8')]

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

    def send_message(self, chat_id, text):
        """

        :param chat_id: Sync ID or Chat ID/Group Chat ID
        :param text:
        :return:
        """
        if isinstance(chat_id, SyncID):
            response_result = ResponseCommandResult(body=text)
            response = ResponseCommand(
                sync_id=chat_id, bot_id=self.bot_id,
                command_result=response_result).to_dict()
            print(response)
            try:
                requests.post(self.url_command, json=response)
            except requests.RequestException as err:
                # @TODO: delete prints
                print(err)
        elif isinstance(chat_id, str) or isinstance(chat_id, list):
            pass
        else:
            raise ValueError('`chat_id` must be of type str or list of str, '
                             'or SyncID object (Message.chat_id)')
