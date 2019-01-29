import json

from collections import OrderedDict

from botx.types.command import Command

from botx.types.job import Job
from botx.types.status import Status, StatusResult
from botx.types.message import Message


class Dispatcher:

    def __init__(self, bot=None):
        self._bot = bot
        self._handlers = OrderedDict()
        # @IDEA: Пользователь в коде пишет register_next_step_handler(user_id)
        # и эта функция берет и добавляет в Dispatcher.handlers новый
        # Command или другой какой-то объект (или вообще 2 тип handlers
        # сделать). Потом, когда parse_request будет вызывать handlers для
        # сверки с пришедшим сообщением, и если там оказывается нужное - тупо
        # запускать нужную функцию и похер что там пришло.

    def parse_request(self, env):
        incoming_content_type = env.get('CONTENT_TYPE')
        incoming_request_method = env.get('REQUEST_METHOD')
        incoming_path_info = env.get('PATH_INFO')
        # incoming_query_string = env.get('QUERY_STRING')

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
            # @TODO: Add status
            return self._create_status(incoming_data)

        if str(incoming_request_method).lower() == 'post' \
                and (str(incoming_path_info).lower() == '/command'
                     or str(incoming_path_info).lower() == '/command/'):
            return self._create_message(incoming_data)

        return

    def _create_status(self, incoming_data=None):
        if not incoming_data:
            return

        incoming_data_bot_id = incoming_data.get('bot_id')
        if not incoming_data_bot_id \
                or incoming_data_bot_id != self._bot.bot_id:
            return

        commands = []
        for _handler_name in self._handlers:
            command = self._handlers.get(_handler_name)
            if isinstance(command, Command):
                commands.append(command.to_dict())
        status_result = StatusResult(commands=commands).__dict__
        status = Status(result=status_result)

        print(status)

        return Job(command=None, message=None, status=Status(status=status))

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
        if not message.chat_id or (not message.text and not message.data):
            return

        # @TODO: make support for data (currently only message.text)
        # @TODO: make case insensitive, improve command detection

        try:
            command_text = message.text.strip().split(' ')[0]
        except (ValueError, IndexError):
            return

        command = self._handlers.get(command_text)
        if isinstance(command, Command):
            return Job(command=command, message=message)
        else:
            any_command = self._handlers.get(Command.ANY)
            if isinstance(any_command, Command):
                return Job(command=any_command, message=message)
            return

    def add_handler(self, handler=None):
        """
        :param handler: A handler with assigned command and function
         :type handler: Command
        :return:
        """
        if not handler or not isinstance(handler, Command):
            raise ValueError('`Command` object must be provided')

        self._handlers.update([(handler.command, handler)])
