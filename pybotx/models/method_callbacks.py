from typing import Any, Literal
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel


class BotAPIMethodSuccessfulCallback(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["ok"]
    result: dict[str, Any]


class BotAPIMethodFailedCallback(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["error"]
    reason: str
    errors: list[str]
    error_data: dict[str, Any]


BotXMethodCallback = BotAPIMethodSuccessfulCallback | BotAPIMethodFailedCallback
