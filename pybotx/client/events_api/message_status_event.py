from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.event import EventNotFoundError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.message.message_status import MessageStatus


class BotXAPIMessageStatusRequestPayload(UnverifiedPayloadBaseModel):
    sync_id: UUID

    @classmethod
    def from_domain(cls, sync_id: UUID) -> "BotXAPIMessageStatusRequestPayload":
        return cls(sync_id=sync_id)


@dataclass
class BotXAPIMessageStatusReadUser:
    user_huid: UUID
    read_at: datetime


@dataclass
class BotXAPIMessageStatusReceivedUser:
    user_huid: UUID
    received_at: datetime


class BotXAPIMessageStatusResult(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sent_to: List[UUID]
    read_by: List[BotXAPIMessageStatusReadUser]
    received_by: List[BotXAPIMessageStatusReceivedUser]


class BotXAPIMessageStatusResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIMessageStatusResult

    def to_domain(self) -> MessageStatus:

        return MessageStatus(
            group_chat_id=self.result.group_chat_id,
            sent_to=self.result.sent_to,
            read_by={
                reader.user_huid: reader.read_at for reader in self.result.read_by
            },
            received_by={
                receiver.user_huid: receiver.received_at
                for receiver in self.result.received_by
            },
        )


class MessageStatusMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(EventNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIMessageStatusRequestPayload,
    ) -> "BotXAPIMessageStatusResponsePayload":
        path = f"/api/v3/botx/events/{payload.sync_id}/status"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIMessageStatusResponsePayload,
            response,
        )
