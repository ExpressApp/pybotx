import multiprocessing

import requests
from typing import Any, BinaryIO, Dict, List, NoReturn, Optional, TextIO, Union
from uuid import UUID

from botx.types import (
    BubbleElement,
    KeyboardElement,
    ResponseCommand,
    ResponseCommandResult,
    ResponseFile,
    ResponseNotification,
    ResponseNotificationResult,
    ResponseRecipientsEnum,
    Status,
    SyncID,
)
from .basebot import BaseBot
from .dispatcher.syncdispatcher import SyncDispatcher


class SyncBot(BaseBot):
    bot_id: UUID
    bot_host: str
    _dispatcher: SyncDispatcher
    _workers: Optional[int] = multiprocessing.cpu_count()

    def __init__(self):
        super().__init__()

        self._dispatcher = SyncDispatcher(workers=self._workers)

    def start(self) -> NoReturn:
        self._dispatcher.start()

    def stop(self) -> NoReturn:
        self._dispatcher.shutdown()

    def parse_status(self) -> Status:
        return self._dispatcher.parse_request({}, request_type="status")

    def parse_command(self, data: Dict[str, Any]) -> bool:
        return self._dispatcher.parse_request(data, request_type="command")

    def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> str:
        if not bubble:
            bubble = []
        if not keyboard:
            keyboard = []

        if isinstance(chat_id, SyncID):
            return self._send_command_result(
                text=text,
                chat_id=chat_id,
                bot_id=bot_id,
                host=host,
                recipients=recipients,
                bubble=bubble,
                keyboard=keyboard,
            )
        elif isinstance(chat_id, UUID) or isinstance(chat_id, list):
            group_chat_ids = []
            if isinstance(chat_id, UUID):
                group_chat_ids.append(chat_id)
            elif isinstance(chat_id, list):
                group_chat_ids = chat_id

            return self._send_notification_result(
                text=text,
                group_chat_ids=group_chat_ids,
                bot_id=bot_id,
                host=host,
                recipients=recipients,
                bubble=bubble,
                keyboard=keyboard,
            )

    def _send_command_result(
        self,
        text: str,
        chat_id: SyncID,
        bot_id: UUID,
        host: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> str:
        response_result = ResponseCommandResult(
            body=text, bubble=bubble, keyboard=keyboard
        )

        response = ResponseCommand(
            bot_id=bot_id,
            sync_id=str(chat_id),
            command_result=response_result,
            recipients=recipients,
        )
        resp = requests.post(self._url_command.format(host), json=response.dict())
        return resp.text

    def _send_notification_result(
        self,
        text: str,
        group_chat_ids: List[UUID],
        bot_id: UUID,
        host: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> str:
        response_result = ResponseNotificationResult(
            body=text, bubble=bubble, keyboard=keyboard
        )
        response = ResponseNotification(
            bot_id=bot_id,
            notification=response_result,
            group_chat_ids=group_chat_ids,
            recipients=recipients,
        )
        resp = requests.post(self._url_notification.format(host), json=response.dict())
        return resp.text

    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> str:
        files = {"file": file}
        response = ResponseFile(bot_id=bot_id, sync_id=chat_id).dict()

        return requests.post(
            self._url_file.format(host), files=files, data=response
        ).text
