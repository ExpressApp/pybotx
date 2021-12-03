from typing import Any, Dict, List, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440

from uuid import UUID

from botx.models.api_base import VerifiedPayloadBaseModel


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
