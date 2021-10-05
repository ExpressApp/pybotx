from typing import Any, Dict, List, NoReturn, Optional
from uuid import UUID

import httpx

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.exceptions.http import RateLimitReachedError
from botx.client.missing import Missing, MissingOptional
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIInternalBotNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    data: Dict[str, Any]
    opts: Missing[Dict[str, Any]]
    recipients: MissingOptional[List[UUID]]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        data: Dict[str, Any],
        opts: Missing[Dict[str, Any]],
        recipients: MissingOptional[List[UUID]],
    ) -> "BotXAPIInternalBotNotificationRequestPayload":
        return cls(
            group_chat_id=chat_id,
            data=data,
            opts=opts,
            recipients=recipients,
        )


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPIInternalBotNotificationResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


def rate_limit_reached_error_status_handler(response: httpx.Response) -> NoReturn:
    raise RateLimitReachedError(response)


class InternalBotNotificationMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        429: rate_limit_reached_error_status_handler,
    }

    async def execute(
        self,
        payload: BotXAPIInternalBotNotificationRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[int],
    ) -> BotXAPIInternalBotNotificationResponsePayload:
        path = "/api/v4/botx/notifications/internal"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        api_model = self._extract_api_model(
            BotXAPIInternalBotNotificationResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
        )

        return api_model
