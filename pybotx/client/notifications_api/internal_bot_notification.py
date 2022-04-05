from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import (
    callback_exception_thrower,
    response_exception_thrower,
)
from pybotx.client.exceptions.common import ChatNotFoundError, RateLimitReachedError
from pybotx.client.exceptions.notifications import (
    BotIsNotChatMemberError,
    FinalRecipientsListEmptyError,
)
from pybotx.missing import Missing, MissingOptional
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


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


class InternalBotNotificationMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        429: response_exception_thrower(RateLimitReachedError),
    }

    error_callback_handlers = {
        **AuthorizedBotXMethod.error_callback_handlers,
        "chat_not_found": callback_exception_thrower(ChatNotFoundError),
        "bot_is_not_a_chat_member": callback_exception_thrower(
            BotIsNotChatMemberError,
        ),
        "event_recipients_list_is_empty": callback_exception_thrower(
            FinalRecipientsListEmptyError,
        ),
    }

    async def execute(
        self,
        payload: BotXAPIInternalBotNotificationRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[float],
        default_callback_timeout: float,
    ) -> BotXAPIInternalBotNotificationResponsePayload:
        path = "/api/v4/botx/notifications/internal"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        api_model = self._verify_and_extract_api_model(
            BotXAPIInternalBotNotificationResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
            default_callback_timeout,
        )

        return api_model
