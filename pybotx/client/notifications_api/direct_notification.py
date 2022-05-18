from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import callback_exception_thrower
from pybotx.client.exceptions.common import ChatNotFoundError
from pybotx.client.exceptions.notifications import (
    BotIsNotChatMemberError,
    FinalRecipientsListEmptyError,
    StealthModeDisabledError,
)
from pybotx.constants import MAX_NOTIFICATION_BODY_LENGTH
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.attachments import (
    BotXAPIAttachment,
    IncomingFileAttachment,
    OutgoingAttachment,
)
from pybotx.models.message.markup import (
    BotXAPIMarkup,
    BubbleMarkup,
    KeyboardMarkup,
    api_markup_from_domain,
)
from pybotx.models.message.mentions import (
    BotXAPIMention,
    find_and_replace_embed_mentions,
)


class BotXAPIDirectNotificationMessageOpts(UnverifiedPayloadBaseModel):
    silent_response: Missing[bool]
    buttons_auto_adjust: Missing[bool]


class BotXAPIDirectNotificationNestedOpts(UnverifiedPayloadBaseModel):
    send: Missing[bool]
    force_dnd: Missing[bool]


class BotXAPIDirectNotificationOpts(UnverifiedPayloadBaseModel):
    stealth_mode: Missing[bool]
    notification_opts: Missing[BotXAPIDirectNotificationNestedOpts]


class BotXAPIDirectNotification(UnverifiedPayloadBaseModel):
    status: Literal["ok"]
    body: str
    metadata: Missing[Dict[str, Any]]
    opts: Missing[BotXAPIDirectNotificationMessageOpts]
    bubble: Missing[BotXAPIMarkup]
    keyboard: Missing[BotXAPIMarkup]
    mentions: Missing[List[BotXAPIMention]]


class BotXAPIDirectNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    notification: BotXAPIDirectNotification
    file: Missing[BotXAPIAttachment]
    recipients: Missing[List[UUID]]
    opts: Missing[BotXAPIDirectNotificationOpts]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]],
        bubbles: Missing[BubbleMarkup],
        keyboard: Missing[KeyboardMarkup],
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]],
        recipients: Missing[List[UUID]],
        silent_response: Missing[bool],
        markup_auto_adjust: Missing[bool],
        stealth_mode: Missing[bool],
        send_push: Missing[bool],
        ignore_mute: Missing[bool],
    ) -> "BotXAPIDirectNotificationRequestPayload":
        api_file: Missing[BotXAPIAttachment] = Undefined
        if file:
            api_file = BotXAPIAttachment.from_file_attachment(file)

        if len(body) > MAX_NOTIFICATION_BODY_LENGTH:
            raise ValueError(
                f"Message body length exceeds {MAX_NOTIFICATION_BODY_LENGTH} symbols",
            )

        body, mentions = find_and_replace_embed_mentions(body)

        return cls(
            group_chat_id=chat_id,
            notification=BotXAPIDirectNotification(
                status="ok",
                body=body,
                metadata=metadata,
                opts=BotXAPIDirectNotificationMessageOpts(
                    silent_response=silent_response,
                    buttons_auto_adjust=markup_auto_adjust,
                ),
                bubble=api_markup_from_domain(bubbles) if bubbles else bubbles,
                keyboard=api_markup_from_domain(keyboard) if keyboard else keyboard,
                mentions=mentions or Undefined,
            ),
            file=api_file,
            recipients=recipients,
            opts=BotXAPIDirectNotificationOpts(
                stealth_mode=stealth_mode,
                notification_opts=BotXAPIDirectNotificationNestedOpts(
                    send=send_push,
                    force_dnd=ignore_mute,
                ),
            ),
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
        callback_timeout: Optional[float],
        default_callback_timeout: float,
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
            default_callback_timeout,
        )
        return api_model
