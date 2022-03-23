from typing import Any, Dict, List, Literal, Union
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel


class BotAPIMethodSuccessfulCallback(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["ok"]
    result: Dict[str, Any]


class BotAPIMethodFailedCallback(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["error"]
    reason: str
    errors: List[str]
    error_data: Dict[str, Any]


BotXMethodCallback = Union[BotAPIMethodSuccessfulCallback, BotAPIMethodFailedCallback]
