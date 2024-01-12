from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.enums import BotAPISystemEventTypes


@dataclass
class EventEdit(BotCommandBase):
    """Event `system:event_edit`.

    Attributes:
        body: updated message body.
    """

    body: Optional[str]


class BotAPIEventEditData(VerifiedPayloadBaseModel):
    body: Optional[str]


class BotAPIEventEditPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_EDIT]
    data: BotAPIEventEditData


class BotAPIEventEdit(BotAPIBaseCommand):
    payload: BotAPIEventEditPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> EventEdit:
        return EventEdit(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            body=self.payload.data.body,
        )
