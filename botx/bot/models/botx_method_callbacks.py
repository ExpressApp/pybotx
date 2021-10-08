from typing import Any, Dict, List, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440

from uuid import UUID

from botx.shared_models.api_base import VerifiedPayloadBaseModel


class BotXMethodCallbackSuccessful(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["ok"]
    result: Dict[str, Any]


class BotXMethodCallbackFailed(VerifiedPayloadBaseModel):
    sync_id: UUID
    status: Literal["error"]
    reason: str
    errors: List[str]
    error_data: Dict[str, Any]


BotXMethodCallback = Union[BotXMethodCallbackSuccessful, BotXMethodCallbackFailed]
