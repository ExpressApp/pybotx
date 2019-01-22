import json

from collections import OrderedDict

from botx.core.commandhandler import CommandHandler

from botx.types.job import Job
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
            return Job(status=True)

        if str(incoming_request_method).lower() == 'post' \
                and (str(incoming_path_info).lower() == '/command'
                     or str(incoming_path_info).lower() == '/command/'):
            return self._create_message(incoming_data)

        return

    def _create_status(self, incoming_data=None):
        if not incoming_data:
            return

        incoming_data_bot_id = incoming_data.get('bot_id')
        if not incoming_data_bot_id or incoming_data_bot_id != self._bot.token:
            return

        # return Job(func_name=None, message=None, status=status), status
        # сгенерировать из self.handlers

    def _create_message(self, incoming_data=None):
        if not incoming_data:
            return

        incoming_data_bot_id = incoming_data.get('bot_id')
        if not incoming_data_bot_id or incoming_data_bot_id != self._bot.token:
            return

        incoming_data_sync_id = incoming_data.get('sync_id')
        incoming_data_command = incoming_data.get('command')

        if not incoming_data_command:
            return

        incoming_data_command_body = incoming_data_command.get('body')
        incoming_data_command_data = incoming_data_command.get('data')

        if not incoming_data_command_body and not incoming_data_command_data:
            return

        incoming_data_from = incoming_data.get('from')

        if not incoming_data_from:
            return

        incoming_data_from_user_id = incoming_data_from.get('user_huid')
        incoming_data_from_group_chat_id = \
            incoming_data_from.get('group_chat_id')

        if not incoming_data_from_user_id \
                or not incoming_data_from_group_chat_id:
            return

        incoming_data_from_ad_login = incoming_data_from.get('ad_login')
        incoming_data_from_host = incoming_data_from.get('host')

        if incoming_data_sync_id and incoming_data_from_ad_login \
                and incoming_data_from_host:
            message = Message(sync_id=incoming_data_sync_id,
                              text=incoming_data_command_body,
                              data=incoming_data_command_data,
                              user_id=incoming_data_from_user_id,
                              user_login=incoming_data_from_ad_login,
                              group_chat_id=incoming_data_from_group_chat_id,
                              host=incoming_data_from_host,
                              bot_id=incoming_data_bot_id)
            try:
                command_text = incoming_data_command_body.strip().split(' ')[0]
            except (ValueError, IndexError):
                return
            command = self._handlers.get(command_text)
            # @TODO: make case insensitive, improve command detection
            if isinstance(command, CommandHandler):
                return Job(command=command, message=message)
            else:
                return
        else:
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
