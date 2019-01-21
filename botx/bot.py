import sys
import signal

import gevent.monkey
gevent.monkey.patch_all()

import gevent.signal

from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from botx.types.job import Job
from botx.types.message import Message
from botx.core.dispatcher import Dispatcher


class Bot:

    def __init__(self, token=None, base_url=None):
        """
        :param token: id (uuid) - an unique identifier in BotX system
         :type token: str
        :param base_url: url
         :type base_url: str
        """

        if not token or not base_url:
            raise ValueError('`token` and `base_url` must be provided')

        self.token = token
        self.url_command = str(base_url) + '/api/v2/botx/command/callback'
        self.url_notification = str(base_url) \
                                + '/api/v2/botx/notification/callback'
        self.url_file = str(base_url) + '/api/v1/botx/file/callback'
        self.dispatcher = Dispatcher(bot=self)
        self._server = None
        self._jobs_queue = Queue()
        self._workers = []

    def start_webhook(self, address='127.0.0.1', port=5000, certfile=None,
                      keyfile=None):
        if not self._server:
            gevent.signal(signal.SIGINT, self.stop_webhook)
            self._start_webhook(address, port, certfile, keyfile)
            self._add_workers()
            self._invoke_workers()

    def _start_webhook(self, address='127.0.0.1', port=5000, certfile=None,
                       keyfile=None):
        if certfile and keyfile:
            server = WSGIServer((address, port), self._webhook_handle,
                                certfile=certfile, keyfile=keyfile)
        else:
            server = WSGIServer((address, port), self._webhook_handle)
        self._server = server
        self._server.start()

    def stop_webhook(self):
        self._server.stop()
        self._server = None
        sys.exit(signal.SIGINT)
        # @TODO: kill all greenlets (self._kill_workers)

    def _webhook_handle(self, env, start_response):
        headers = [('Content-Type', 'application/json')]
        response_ok = '200 OK'
        response_accepted = '202 Accepted'
        # Parse a request
        # Generate a Job
        job = self.dispatcher.parse_request(env)
        print('handle job {}'.format(job))
        if job and isinstance(job, Job) and isinstance(job.message, Message):
            self._jobs_queue.put_nowait(job)
            start_response(response_accepted, headers)
            return [b'{"status": "ok"}']
        else:
            # @TODO: send a status
            pass
        start_response(response_ok, headers)
        return [b'{"status": "ok"}']

    def _add_workers(self, workers_number=4):
        self._workers = []
        for _ in range(workers_number):
            self._workers.append(gevent.spawn(self._process_request_worker))
        # self._workers.append(self._server_worker)
        print(self._workers)

    def _invoke_workers(self):
        gevent.joinall(self._workers)

    def _kill_workers(self):
        pass

    def _process_request_worker(self):
        print('Worker started')
        while True:
            job = None
            try:
                job = self._jobs_queue.get_nowait()
                print('a job {}'.format(job))
            except gevent.queue.Empty:
                pass
            if job and isinstance(job, Job):
                print('{} {}'.format(job.command, job.message))
                job.command.func(job.message)
            gevent.sleep(0)

    def send_message(self, chat_id, text):
        pass
