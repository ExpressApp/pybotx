from dataclasses import dataclass
from typing import Dict, Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.models.bot_account import BotAccount
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import BotCommandBase, BaseBotAPIContext, BotAPIBaseCommand, \
    BotAPIBaseSystemEventPayload
from pybotx.models.enums import BotAPISystemEventTypes


@dataclass
class EventDelete(BotCommandBase):
    """Event `system:event_delete`.

    Attributes:
        sync_id: ID of the deleted message.
    """

    sync_id: UUID


class BotAPIEventDeleteData(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotAPIEventDeletePayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_DELETE]
    data: BotAPIEventDeleteData


class BotAPIEventDelete(BotAPIBaseCommand):
    payload: BotAPIEventDeletePayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> EventDelete:
        return EventDelete(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            sync_id=self.sync_id,
            raw_command=raw_command
        )
