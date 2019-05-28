import json
import logging
import multiprocessing
from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Tuple, Union, cast
from uuid import UUID

import requests

from botx.core import BotXException
from botx.types import (
    BotCredentials,
    BubbleElement,
    CTSCredentials,
    File,
    KeyboardElement,
    Mention,
    Message,
    ResponseCommand,
    ResponseFile,
    ResponseNotification,
    ResponseRecipientsEnum,
    ResponseResult,
    Status,
    SyncID,
)

from .base_bot import BaseBot
from .dispatcher.sync_dispatcher import SyncDispatcher

LOGGER = logging.getLogger("botx")


class SyncBot(BaseBot):
    _dispatcher: SyncDispatcher
    _session: requests.Session

    def __init__(
        self,
        *,
        workers: int = multiprocessing.cpu_count(),
        credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False,
    ):
        super().__init__(
            credentials=credentials, disable_credentials=disable_credentials
        )

        self._dispatcher = SyncDispatcher(workers=workers, bot=self)
        self._session = requests.Session()

    def start(self):
        self._dispatcher.start()

    def stop(self):
        self._dispatcher.shutdown()
        self._session.close()

    def parse_status(self) -> Status:
        return cast(Status, self._dispatcher.parse_request({}, request_type="status"))

    def parse_command(self, data: Dict[str, Any]) -> bool:
        return cast(bool, self._dispatcher.parse_request(data, request_type="command"))

    def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> Tuple[str, int]:
        if not bubble:
            bubble = []
        if not keyboard:
            keyboard = []
        if not mentions:
            mentions = []

        token = self._get_token_from_cts(host)
        if not token and not self._disable_credentials:
            res = self._obtain_token(host, bot_id)
            if res[1] != 200:
                return res

        response_file = File.from_file(file) if file else None

        if isinstance(chat_id, SyncID):
            return self._send_command_result(
                text=text,
                chat_id=chat_id,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
            )

        if isinstance(chat_id, (UUID, list)):
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
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
            )

        raise BotXException(f"{type(chat_id)} is not accessible for chat_id argument")

    def answer_message(
        self,
        text: str,
        message: Message,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> Tuple[str, int]:
        return self.send_message(
            text,
            message.sync_id,
            message.bot_id,
            message.host,
            file=file,
            recipients=recipients,
            mentions=mentions,
            bubble=bubble,
            keyboard=keyboard,
        )

    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> Tuple[str, int]:
        token = self._get_token_from_cts(host)
        if not token and not self._disable_credentials:
            res = self._obtain_token(host, bot_id)
            if res[1] != 200:
                return res

        files = {"file": file}
        response = ResponseFile(bot_id=bot_id, sync_id=chat_id).dict()

        LOGGER.debug("sending file to BotX on %r", host)

        resp = self._session.post(
            self._url_file.format(host=host),
            files=files,
            data=response,
            headers={"Authorization": f"Bearer {token}"},
        )
        return resp.text, resp.status_code

    def _obtain_token(self, host: str, bot_id: UUID) -> Tuple[str, int]:
        cts = self.get_cts_by_host(host)
        if not cts:
            raise BotXException(f"unregistered cts with host {repr(host)}")

        signature = cts.calculate_signature(bot_id)

        LOGGER.debug("obtaining token for operations from BotX API on %r", cts.host)

        resp = self._session.get(
            self._url_token.format(host=host, bot_id=bot_id),
            params={"signature": signature},
        )
        if resp.status_code != 200:
            LOGGER.debug("can not obtain token")
            return resp.text, resp.status_code

        token = json.loads(resp.text).get("result")

        cts.credentials = CTSCredentials(bot_id=bot_id, token=token)
        self._set_cts_credentials(cts)

        return resp.text, resp.status_code

    def _send_command_result(
        self,
        text: str,
        chat_id: SyncID,
        bot_id: UUID,
        host: str,
        file: Optional[File],
        recipients: Union[List[UUID], str],
        mentions: List[Mention],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Tuple[str, int]:
        response_result = ResponseResult(
            body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
        )

        response = ResponseCommand(
            bot_id=bot_id,
            sync_id=str(chat_id),
            command_result=response_result,
            recipients=recipients,
            file=file,
        )

        LOGGER.debug("sending command result to BotX on %r: %r", host, response.json())

        resp = self._session.post(
            self._url_command.format(host=host),
            json=response.dict(),
            headers={"Authorization": f"Bearer {self._get_token_from_cts(host)}"},
        )
        return resp.text, resp.status_code

    def _send_notification_result(
        self,
        text: str,
        group_chat_ids: List[UUID],
        bot_id: UUID,
        host: str,
        file: Optional[File],
        recipients: Union[List[UUID], str],
        mentions: List[Mention],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Tuple[str, int]:
        response_result = ResponseResult(
            body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
        )
        response = ResponseNotification(
            bot_id=bot_id,
            notification=response_result,
            group_chat_ids=group_chat_ids,
            recipients=recipients,
            file=file,
        )

        LOGGER.debug(
            "sending notification result to BotX on %r: %r", host, response.json()
        )

        resp = self._session.post(
            self._url_notification.format(host=host),
            json=response.dict(),
            headers={"Authorization": f"Bearer {self._get_token_from_cts(host)}"},
        )
        return resp.text, resp.status_code
