import json
from typing import Any, BinaryIO, Dict, List, NoReturn, Optional, TextIO, Tuple, Union
from uuid import UUID

import aiohttp

from botx.core import BotXException
from botx.types import (
    BotCredentials,
    BubbleElement,
    CTSCredentials,
    File,
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
from .dispatcher.asyncdispatcher import AsyncDispatcher


class AsyncBot(BaseBot):
    bot_id: UUID
    bot_host: str
    _session: aiohttp.ClientSession

    def __init__(self, *, credentials: Optional[BotCredentials] = None):
        super().__init__(credentials=credentials)

        self._dispatcher = AsyncDispatcher()
        self._session = aiohttp.ClientSession()

    async def start(self) -> NoReturn:
        await self._dispatcher.start()

    async def stop(self) -> NoReturn:
        await self._dispatcher.shutdown()

    async def parse_status(self) -> Status:
        return await self._dispatcher.parse_request({}, request_type="status")

    async def parse_command(self, data: Dict[str, Any]) -> bool:
        return await self._dispatcher.parse_request(data, request_type="command")

    async def _obtain_token(self, host: str, bot_id: UUID) -> Tuple[str, int]:
        if host not in self._credentials.known_cts:
            raise BotXException(f"unregistered cts with host {repr(host)}")

        cts = self._credentials.known_cts[host][0]
        signature = cts.calculate_signature(bot_id)

        async with self._session.get(
            self._url_token.format(host=host, bot_id=bot_id),
            params={"signature": signature},
        ) as resp:
            text = await resp.text()
            if resp.status != 200:
                return text, resp.status

            token = json.loads(text).get("token")
            self._credentials.known_cts[host] = (
                cts,
                CTSCredentials(bot_id=bot_id, token=token),
            )

            return text, resp.status

    async def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> Tuple[str, int]:
        if not bubble:
            bubble = []
        if not keyboard:
            keyboard = []

        token = self._get_token_from_credentials(host)
        if not token:
            res = await self._obtain_token(host, bot_id)
            if res[1] != 200:
                return res

        response_file = File.from_file(file) if file else None

        if isinstance(chat_id, SyncID):
            return await self._send_command_result(
                text=text,
                chat_id=chat_id,
                bot_id=bot_id,
                host=host,
                file=response_file,
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

            return await self._send_notification_result(
                text=text,
                group_chat_ids=group_chat_ids,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                bubble=bubble,
                keyboard=keyboard,
            )

    async def _send_command_result(
        self,
        text: str,
        chat_id: SyncID,
        bot_id: UUID,
        host: str,
        file: Optional[Union[BinaryIO, TextIO]],
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Tuple[str, int]:
        response_result = ResponseCommandResult(
            body=text, bubble=bubble, keyboard=keyboard
        )

        response = ResponseCommand(
            bot_id=bot_id,
            sync_id=str(chat_id),
            command_result=response_result,
            recipients=recipients,
            file=file,
        ).dict()

        async with self._session.post(
            self._url_command.format(host=host),
            json=response,
            headers={
                "Authorization": f"Bearer {self._get_token_from_credentials(host)}"
            },
        ) as resp:
            return await resp.text(), resp.status

    async def _send_notification_result(
        self,
        text: str,
        group_chat_ids: List[UUID],
        bot_id: UUID,
        host: str,
        file: Optional[Union[BinaryIO, TextIO]],
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Tuple[str, int]:
        response_result = ResponseNotificationResult(
            body=text, bubble=bubble, keyboard=keyboard
        )
        response = ResponseNotification(
            bot_id=bot_id,
            notification=response_result,
            group_chat_ids=group_chat_ids,
            recipients=recipients,
            file=file,
        ).dict()

        async with self._session.post(
            self._url_notification.format(host=host),
            json=response,
            headers={
                "Authorization": f"Bearer {self._get_token_from_credentials(host)}"
            },
        ) as resp:
            return await resp.text(), resp.status

    async def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> Tuple[str, int]:
        token = self._get_token_from_credentials(host)
        if not token:
            res = await self._obtain_token(host, bot_id)
            if res[1] != 200:
                return res

        response = ResponseFile(bot_id=bot_id, sync_id=chat_id, file=file).dict()
        response["file"] = file

        async with self._session.post(
            self._url_file.format(host=host),
            data=response,
            headers={
                "Authorization": f"Bearer {self._get_token_from_credentials(host)}"
            },
        ) as resp:
            return await resp.text(), resp.status
