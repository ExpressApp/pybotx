from typing import Any, Dict, List, Union
from uuid import UUID

from botx.bot.models.outgoing_attachment import OutgoingAttachment
from botx.client.attachments import BotXAPIAttachment
from botx.client.authorized_botx_method import AuthorizedBotXMethod
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
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from botx.shared_models.domain.attachments import IncomingFileAttachment

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIDirectNotification(UnverifiedPayloadBaseModel):
    status: Literal["ok"]
    body: str
    metadata: Missing[Dict[str, Any]]
    bubbles: Missing[BotXAPIMarkup]
    keyboard: Missing[BotXAPIMarkup]
    mentions: Missing[List[BotXAPIMention]]


class BotXAPIDirectNotificationOptions(UnverifiedPayloadBaseModel):
    raw_mentions: bool = False  # TODO: Delete in v4


class BotXAPIDirectNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    recipients: Literal["all"]
    notification: BotXAPIDirectNotification
    file: Missing[BotXAPIAttachment]
    opts: Missing[BotXAPIDirectNotificationOptions]

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

        opts: Missing[BotXAPIDirectNotificationOptions] = Undefined
        if mentions:
            opts = BotXAPIDirectNotificationOptions(raw_mentions=True)

        return cls(
            group_chat_id=chat_id,
            recipients="all",
            notification=BotXAPIDirectNotification(
                status="ok",
                body=body,
                metadata=metadata,
                bubbles=api_markup_from_domain(bubbles) if bubbles else bubbles,
                keyboard=api_markup_from_domain(keyboard) if keyboard else keyboard,
                mentions=mentions or Undefined,
            ),
            file=api_file,
            opts=opts,
        )


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPIDirectNotificationResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class DirectNotificationMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIDirectNotificationRequestPayload,
    ) -> BotXAPIDirectNotificationResponsePayload:
        path = "/api/v3/botx/notification/callback/direct"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIDirectNotificationResponsePayload,
            response,
        )
