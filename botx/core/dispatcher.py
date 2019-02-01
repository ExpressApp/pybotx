import json

from urllib.parse import parse_qs
from collections import OrderedDict

from botx.core.commandhandler import CommandHandler

from botx.types.job import Job
from botx.types.status import Status, StatusResult
from botx.types.message import Message


class Dispatcher:

    def __init__(self, bot=None):
        self._bot = bot
        self._handlers = OrderedDict()
        # @IDEA: Пользователь в коде пишет register_next_step_handler(user_id)
        # и эта функция берет и добавляет в Dispatcher.handlers новый
        # CommandHandler или другой какой-то объект (или вообще 2 тип handlers
        # сделать). Потом, когда parse_request будет вызывать handlers для
        # сверки с пришедшим сообщением, и если там оказывается нужное - тупо
        # запускать нужную функцию и похер что там пришло.

    def parse_request(self, env):
        incoming_content_type = env.get('CONTENT_TYPE')
        incoming_request_method = env.get('REQUEST_METHOD')
        incoming_path_info = env.get('PATH_INFO')
        incoming_query_string = env.get('QUERY_STRING')

        incoming_data = None
        if str(incoming_content_type).lower() == 'application/json':
            incoming_data = env.get('wsgi.input').read().decode('utf-8') \
                                                        .replace("'", '"')
            if incoming_data:
                incoming_data = json.loads(incoming_data)
            else:
                incoming_data = None

        if str(incoming_request_method).lower() == 'get' \
                and (str(incoming_path_info).lower() == '/status'
                     or str(incoming_path_info).lower() == '/status/'):
            return self._create_status(incoming_query_string)

        if str(incoming_request_method).lower() == 'post' \
                and (str(incoming_path_info).lower() == '/command'
                     or str(incoming_path_info).lower() == '/command/'):
            return self._create_message(incoming_data)

        return

    def _create_status(self, incoming_data=None):
        if not incoming_data:
            return

        incoming_data = parse_qs(incoming_data)
        try:
            incoming_data_bot_id = incoming_data.get('bot_id')[0]
        except IndexError:
            incoming_data_bot_id = None

        if not incoming_data_bot_id \
                or incoming_data_bot_id != self._bot.bot_id:
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

        return Job(command=None, message=None, status=status)

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
        # @TODO: make case insensitive, improve command detection

        try:
            command_text = message.body.strip().split(' ')[0]
        except (ValueError, IndexError):
            return

        command = self._handlers.get(command_text)
        if isinstance(command, CommandHandler):
            return Job(command=command, message=message)
        else:
            any_command = self._handlers.get(CommandHandler.ANY)
            if isinstance(any_command, CommandHandler):
                return Job(command=any_command, message=message)
            return

    def add_handler(self, handler=None):
        """
        :param handler: A handler with assigned command and function
         :type handler: CommandHandler
        :return:
        """
        if not handler or not isinstance(handler, CommandHandler):
            raise ValueError('`CommandHandler` object must be provided')

        self._handlers.update([(handler.command, handler)])
