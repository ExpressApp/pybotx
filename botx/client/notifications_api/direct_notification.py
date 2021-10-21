from typing import Any, Dict, Union
from uuid import UUID

from botx.bot.models.outgoing_attachment import OutgoingAttachment
from botx.client.attachments import BotXAPIAttachment
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.missing import Missing, Undefined
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from botx.shared_models.domain.attachments import IncomingContentAttachment

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIDirectNotification(UnverifiedPayloadBaseModel):
    status: Literal["ok"]
    body: str
    metadata: Missing[Dict[str, Any]]


class BotXAPIDirectNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    recipients: Literal["all"]
    notification: BotXAPIDirectNotification
    file: Missing[BotXAPIAttachment]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]],
        file: Missing[Union[IncomingContentAttachment, OutgoingAttachment]],
    ) -> "BotXAPIDirectNotificationRequestPayload":
        return cls(
            group_chat_id=chat_id,
            recipients="all",
            notification=BotXAPIDirectNotification(
                status="ok",
                body=body,
                metadata=metadata,
            ),
            file=(BotXAPIAttachment.from_file_attachment(file) if file else Undefined),
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

        return self._extract_api_model(
            BotXAPIDirectNotificationResponsePayload,
            response,
        )
