from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.shared_models.api_base import APIBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPINotification(APIBaseModel):
    status: Literal["ok"]
    body: str


class BotXAPIDirectNotificationPayload(APIBaseModel):
    group_chat_id: UUID
    recipients: Literal["all"]
    notification: BotXAPINotification

    @classmethod
    def from_domain(
        cls,
        body: str,
        chat_id: UUID,
    ) -> "BotXAPIDirectNotificationPayload":
        return cls(
            group_chat_id=chat_id,
            recipients="all",
            notification=BotXAPINotification(
                status="ok",
                body=body,
            ),
        )


class BotXAPISyncIdResult(APIBaseModel):
    sync_id: UUID


class BotXAPISyncId(APIBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class DirectNotificationMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPIDirectNotificationPayload) -> BotXAPISyncId:
        path = "/api/v3/botx/notification/callback/direct"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            content=payload.json(),
        )

        return self._extract_api_model(BotXAPISyncId, response)
