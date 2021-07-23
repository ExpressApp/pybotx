"""Definition of errors in processing request from BotX API."""

from typing import List

from botx.models.base import BotXBaseModel


class BotDisabledErrorData(BotXBaseModel):
    """Data about occurred error."""

    #: message that will be shown to user.
    status_message: str


class BotDisabledResponse(BotXBaseModel):
    """Response to BotX API if there was an error in handling incoming request."""

    #: error reason. *This should always be `bot_disabled` string.*
    reason: str = "bot_disabled"

    #: data about occurred error that should include `status_message` field in json.
    error_data: BotDisabledErrorData

    errors: List[str] = []
