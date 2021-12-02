from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import callback_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError
from botx.client.notifications_api.exceptions import (
    BotIsNotChatMemberError,
    FinalRecipientsListEmptyError,
    StealthModeDisabledError,
)
from botx.client.notifications_api.markup import (
    BotXAPIMarkup,
    BubbleMarkup,
    KeyboardMarkup,
    api_markup_from_domain,
)
from botx.client.notifications_api.mentions import (
    BotXAPIMention,
    find_and_replace_embed_mentions,
)
from botx.missing import Missing, Undefined
from botx.models.attachments import (
    BotXAPIAttachment,
    IncomingFileAttachment,
    OutgoingAttachment,
)
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIDirectNotification(UnverifiedPayloadBaseModel):
    status: Literal["ok"]
    body: str
    metadata: Missing[Dict[str, Any]]
    bubble: Missing[BotXAPIMarkup]
    keyboard: Missing[BotXAPIMarkup]
    mentions: Missing[List[BotXAPIMention]]


class BotXAPIDirectNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    notification: BotXAPIDirectNotification
    file: Missing[BotXAPIAttachment]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]],
        bubbles: Missing[BubbleMarkup],
        keyboard: Missing[KeyboardMarkup],
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]],
    ) -> "BotXAPIDirectNotificationRequestPayload":
        api_file: Missing[BotXAPIAttachment] = Undefined
        if file:
            assert not file.is_async_file, "async_files not supported"
            api_file = BotXAPIAttachment.from_file_attachment(file)

        body, mentions = find_and_replace_embed_mentions(body)

        return cls(
            group_chat_id=chat_id,
            notification=BotXAPIDirectNotification(
                status="ok",
                body=body,
                metadata=metadata,
                bubble=api_markup_from_domain(bubbles) if bubbles else bubbles,
                keyboard=api_markup_from_domain(keyboard) if keyboard else keyboard,
                mentions=mentions or Undefined,
            ),
            file=api_file,
        )


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPIDirectNotificationResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class DirectNotificationMethod(AuthorizedBotXMethod):
    error_callback_handlers = {
        **AuthorizedBotXMethod.error_callback_handlers,
        "chat_not_found": callback_exception_thrower(ChatNotFoundError),
        "bot_is_not_a_chat_member": callback_exception_thrower(
            BotIsNotChatMemberError,
        ),
        "event_recipients_list_is_empty": callback_exception_thrower(
            FinalRecipientsListEmptyError,
        ),
        "stealth_mode_disabled": callback_exception_thrower(StealthModeDisabledError),
    }

    async def execute(
        self,
        payload: BotXAPIDirectNotificationRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[int],
    ) -> BotXAPIDirectNotificationResponsePayload:
        path = "/api/v4/botx/notifications/direct"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        api_model = self._verify_and_extract_api_model(
            BotXAPIDirectNotificationResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
        )
        return api_model
