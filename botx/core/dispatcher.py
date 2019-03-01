import json

from collections import OrderedDict

import gevent
from gevent.queue import Queue

from .commandhandler import CommandHandler
from botx.types import Job, Status, StatusResult, Message


class Dispatcher:

    def __init__(self, bot=None):
        self._bot = bot
        self._handlers = OrderedDict()
        self._jobs_queue = Queue()
        self._workers = []
        # @IDEA: Пользователь в коде пишет register_next_step_handler(user_id)
        # и эта функция берет и добавляет в Dispatcher.handlers новый
        # CommandHandler или другой какой-то объект (или вообще 2 тип handlers
        # сделать). Потом, когда parse_request будет вызывать handlers для
        # сверки с пришедшим сообщением, и если там оказывается нужное - тупо
        # запускать нужную функцию и похер что там пришло.

    def add_workers(self, workers_number):
        if not isinstance(workers_number, int):
            raise ValueError('A `workers_number` parameter must be of str '
                             'type')
        if workers_number < 1:
            raise ValueError('A `workers_number` parameter must be equal or '
                             'more than 1')
        self._workers = []
        for _ in range(workers_number):
            self._workers.append(gevent.spawn(self._process_request_worker))

    def _process_request_worker(self):
        while True:
            try:
                job = self._jobs_queue.get()
            except gevent.queue.Empty:
                continue
            if job and isinstance(job, Job) \
                    and isinstance(job.command, CommandHandler)\
                    and isinstance(job.message, Message):
                job.command.func(job.message)

    def parse_request(self, data, type_=None):
        if not isinstance(type_, str):
            raise ValueError('A `type_` parameter is not provided or not of '
                             'str type')

        if data and type_ == 'status':
            return self._create_status(data)
        elif data and type_ == 'command':
            incoming_data = data.decode('utf-8').replace("'", '"')
            if incoming_data:
                incoming_data = json.loads(incoming_data)
            else:
                incoming_data = None
            return self._create_message(incoming_data)
        return

    def _create_status(self, incoming_data=None):
        """
        :param incoming_data: A bot_id
        :return:
        """
        print('create status')
        if not incoming_data or incoming_data != self._bot.bot_id:
            return

        commands = []
        for _handler_name in self._handlers:
            command = self._handlers.get(_handler_name)
            if isinstance(command, CommandHandler):
                if command.is_status_command_compatible:
                    status_command = command.to_status_command()
                    if status_command:
                        commands.append(status_command)
        status_result = StatusResult(commands=commands)
        status = Status(result=status_result)

        print(status.to_dict())
        return status

    def _create_message(self, incoming_data=None):
        if not incoming_data:
            return

        incoming_data_bot_id = incoming_data.get('bot_id')
        if not incoming_data_bot_id \
                or incoming_data_bot_id != self._bot.bot_id:
            return

        message = Message.from_json(incoming_data)
        if not isinstance(message, Message):
            return
        if not message.sync_id or (not message.body and not message.data):
            return

        # @TODO: make support for data (currently only message.body)
        # @TODO: improve command detection

        try:
            command_text = message.body.strip().split(' ')[0]
        except (ValueError, IndexError):
            return

        command = self._handlers.get(command_text.lower())
        if isinstance(command, CommandHandler):
            self._jobs_queue.put(Job(command=command, message=message))
            return True
        else:
            any_command = self._handlers.get(CommandHandler.ANY)
            if isinstance(any_command, CommandHandler):
                self._jobs_queue.put(Job(command=any_command, message=message))
                return True
        return

    def add_handler(self, handler):
        """
        A method to add a command for bot

        :param handler: A handler with assigned command and function
         :type handler: CommandHandler
        :return:
        """
        if not isinstance(handler, CommandHandler):
            raise ValueError('`CommandHandler` object must be provided')

        self._handlers.update([(
            (handler.command.lower() if isinstance(handler.command, str)
             else handler.command), handler)])
