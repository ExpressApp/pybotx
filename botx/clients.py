import abc
import json
from typing import Any, Awaitable, Callable, Dict, Optional
from uuid import UUID

from httpx import AsyncClient
from httpx.models import BaseResponse
from httpx.status_codes import StatusCode
from loguru import logger

from .core import BotXAPI
from .exceptions import BotXAPIException
from .helpers import get_data_for_api_error
from .models import (
    BotXCommandResultPayload,
    BotXFilePayload,
    BotXNotificationPayload,
    BotXResultPayload,
    BotXTokenRequestParams,
    SendingCredentials,
    SendingPayload,
)
from .models.botx_api import BotXPayloadOptions

logger_ctx = logger.bind(botx_client=True)


def get_headers(token: str) -> Dict[str, str]:
    return {"authorization": f"Bearer {token}"}


def check_api_error(resp: BaseResponse) -> bool:
    return StatusCode.is_client_error(resp.status_code) or StatusCode.is_server_error(
        resp.status_code
    )


class BaseBotXClient(abc.ABC):
    _token_url: str = BotXAPI.V2.token.url
    _command_url: str = BotXAPI.V3.command.url
    _notification_url: str = BotXAPI.V3.notification.url
    _file_url: str = BotXAPI.V1.file.url

    @abc.abstractmethod
    def send_file(
        self, address: SendingCredentials, payload: SendingPayload
    ) -> Optional[Awaitable[None]]:
        """Send separate file to BotX API"""

    @abc.abstractmethod
    def obtain_token(self, host: str, bot_id: UUID, signature: str) -> Any:
        """Obtain token from BotX for making requests"""

    @abc.abstractmethod
    def send_command_result(
        self, credentials: SendingCredentials, payload: SendingPayload
    ) -> Optional[Awaitable[None]]:
        """Send handler result answer"""

    @abc.abstractmethod
    def send_notification(
        self, credentials: SendingCredentials, payload: SendingPayload
    ) -> Optional[Awaitable[None]]:
        """Send notification result answer"""


class AsyncBotXClient(BaseBotXClient):
    asgi_app: Optional[Callable] = None

    async def send_file(
        self, credentials: SendingCredentials, payload: SendingPayload
    ) -> None:
        assert payload.file, "payload should include File object"

        async with AsyncClient(app=self.asgi_app) as client:
            logger_ctx.bind(
                credentials=json.loads(credentials.json(exclude={"token", "chat_ids"})),
                payload={"filename": payload.file.file_name},
            ).debug("send file")

            resp = await client.post(
                self._file_url.format(host=credentials.host),
                data=BotXFilePayload.from_orm(credentials).dict(),
                files={"file": payload.file.file},
            )
        if check_api_error(resp):
            raise BotXAPIException(
                "unable to send file to BotX API",
                data=get_data_for_api_error(credentials, resp),
            )

    async def obtain_token(self, host: str, bot_id: UUID, signature: str) -> Any:
        async with AsyncClient(app=self.asgi_app) as client:
            logger_ctx.bind(
                credentials={"host": host, "bot_id": str(bot_id)},
                payload={"signature": signature},
            ).debug("obtain token")

            resp = await client.get(
                self._token_url.format(host=host, bot_id=bot_id),
                params=BotXTokenRequestParams(signature=signature).dict(),
            )
        if check_api_error(resp):
            raise BotXAPIException(
                "unable to obtain token from BotX API",
                data=get_data_for_api_error(
                    SendingCredentials(host=host, bot_id=bot_id, token=""), resp
                ),
            )
        return resp.json()

    async def send_command_result(
        self, credentials: SendingCredentials, payload: SendingPayload
    ) -> None:
        assert credentials.token, "credentials should include access token"

        command_result = BotXCommandResultPayload(
            bot_id=credentials.bot_id,
            sync_id=credentials.sync_id,
            command_result=BotXResultPayload(
                body=payload.text,
                bubble=payload.markup.bubbles,
                keyboard=payload.markup.keyboard,
                mentions=payload.options.mentions,
            ),
            recipients=payload.options.recipients,
            file=payload.file,
            opts=BotXPayloadOptions(notification_opts=payload.options.notifications),
        )

        async with AsyncClient(app=self.asgi_app) as client:
            logger_ctx.bind(
                credentials=json.loads(credentials.json(exclude={"token", "chat_ids"})),
                payload=json.loads(command_result.json()),
            ).debug("send command result")

            resp = await client.post(
                self._command_url.format(host=credentials.host),
                json=command_result.dict(),
                headers=get_headers(credentials.token),
            )
        if check_api_error(resp):
            raise BotXAPIException(
                "unable to send command result to BotX API",
                data=get_data_for_api_error(credentials, resp),
            )

    async def send_notification(
        self, credentials: SendingCredentials, payload: SendingPayload
    ) -> None:
        assert credentials.token, "credentials should include access token"

        notification = BotXNotificationPayload(
            bot_id=credentials.bot_id,
            group_chat_ids=credentials.chat_ids,
            notification=BotXResultPayload(
                body=payload.text,
                bubble=payload.markup.bubbles,
                keyboard=payload.markup.keyboard,
                mentions=payload.options.mentions,
            ),
            recipients=payload.options.recipients,
            file=payload.file,
            opts=BotXPayloadOptions(notification_opts=payload.options.notifications),
        )
        async with AsyncClient(app=self.asgi_app) as client:
            logger.bind(
                credentials=json.loads(credentials.json(exclude={"token", "sync_id"})),
                payload=json.loads(notification.json()),
            ).debug("send notification")

            resp = await client.post(
                self._notification_url.format(host=credentials.host),
                json=notification.dict(),
                headers=get_headers(credentials.token),
            )
        if check_api_error(resp):
            raise BotXAPIException(
                "unable to send notification to BotX API",
                data=get_data_for_api_error(credentials, resp),
            )
