import sys
import signal

import gevent.monkey
gevent.monkey.patch_all()

import requests
import gevent.signal

from botx.core import Dispatcher
from botx.types import SyncID, InputFile, \
    ReplyBubbleMarkup, ReplyKeyboardMarkup, ResponseCommand, \
    ResponseNotification, ResponseCommandResult, ResponseDocument


class Bot:

    def __init__(self, bot_id=None, bot_host=None):
        """
        Initiation of a Bot

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

    def start_bot(self, workers_number=4):
        """
        A method to start webhook

        :param workers_number: A number of workers
         :type workers_number: int
        """
        gevent.signal(signal.SIGINT, Bot.stop_bot)
        self.dispatcher.add_workers(workers_number)

    @staticmethod
    def stop_bot():
        sys.exit(signal.SIGINT)

    def parse_status(self, bot_id):
        """
        :param bot_id: A bot_id
         :type bot_id: str
        :return:
        """
        if not isinstance(bot_id, str):
            raise ValueError('A `bot_id` parameter must be of str type')
        return self.dispatcher.parse_request(bot_id, type_='status')

    def parse_command(self, data):
        """
        :param data: data
         :type data: bytes
        :return:
        """
        if not isinstance(data, bytes):
            raise ValueError('A `data` parameter must be of bytes type')
        self.dispatcher.parse_request(data, type_='command')

    def send_message(self, chat_id, text, recipients='all', bubble=None,
                     keyboard=None):
        """
        A method to send text messages

        :param chat_id: Sync ID or Chat ID/Group Chat ID
         :type chat_id: SyncID, str
        :param text: A text message
         :type text: str
        :param recipients: Recipients
         :type recipients: list, str
        :param bubble: A bubble markup for message
         :type bubble: ReplyBubbleMarkup
        :param keyboard: A keyboard markup
         :type keyboard: ReplyKeyboardMarkup
        """
        if bubble and not isinstance(bubble, ReplyBubbleMarkup):
            raise ValueError('A `bubble` attribute must be of '
                             '`ReplyBubbleMarkup` type')
        if bubble and isinstance(bubble, ReplyBubbleMarkup):
            bubble = bubble.to_list()

        if keyboard and not isinstance(keyboard, ReplyKeyboardMarkup):
            raise ValueError('A `keyboard` attribute must be of '
                             '`ReplyKeyboardMarkup` type')
        if keyboard and isinstance(keyboard, ReplyKeyboardMarkup):
            keyboard = keyboard.to_list()

        if isinstance(chat_id, SyncID):
            response_result = ResponseCommandResult(body=text,
                                                    bubble=bubble,
                                                    keyboard=keyboard)
            response = \
                ResponseCommand(
                    bot_id=self.bot_id,
                    sync_id=chat_id,
                    command_result=response_result,
                    recipients=recipients
                ).to_dict()
            print(response)
            try:
                requests.post(self.url_command, json=response)
            except requests.RequestException as error:
                # @TODO: delete print
                print(error)
        elif isinstance(chat_id, str) or isinstance(chat_id, list):
            group_chat_ids = []
            if isinstance(chat_id, str):
                group_chat_ids.append(chat_id)
            elif isinstance(chat_id, list):
                group_chat_ids = chat_id
            response_result = ResponseCommandResult(body=text,
                                                    bubble=bubble,
                                                    keyboard=keyboard)
            response = \
                ResponseNotification(
                    bot_id=self.bot_id,
                    command_result=response_result,
                    group_chat_ids=group_chat_ids,
                    recipients=recipients
                ).to_dict()
            print(response)
            try:
                requests.post(self.url_notification, json=response)
            except requests.RequestException as error:
                # @TODO: delete print
                print(error)
        else:
            raise ValueError('`chat_id` must be of type str or list of str, '
                             'or SyncID object (Message.chat_id)')

    def send_document(self, chat_id, document):
        """
        A method to send documents (different file types)

        :param chat_id: Sync ID or Chat ID/Group Chat ID
         :type chat_id: SyncID, str
        :param document: A binary document
         :type document: bytearray
        """
        if not InputFile.is_file(document):
            return

        files = {'file': document}
        response = ResponseDocument(bot_id=self.bot_id, sync_id=chat_id)

        try:
            requests.post(self.url_file, files=files, data=response.to_dict())
        except requests.RequestException as error:
            # @TODO: delete print
            print(error)
