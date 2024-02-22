from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal


@dataclass
class BotAPIUnverifiedRequestErrorData:
    status_message: str


@dataclass
class BotAPIUnverifiedRequestResponse:
    """`Unverified request` response model.

    Only `.error_data.status_message` attribute will be displayed to
    user. Other attributes will be visible only in BotX logs.
    """

    error_data: BotAPIUnverifiedRequestErrorData
    errors: List[str] = field(default_factory=list)
    reason: Literal["unverified_request"] = "unverified_request"


def build_unverified_request_response(status_message: str) -> Dict[str, Any]:
    """Build `unverified request` response for BotX.

    It should be sent if the header with the authorization token is missing or
    the authorization token is invalid.
    If you would like to build complex response, see `BotAPIUnverifiedRequestResponse`.

    :param status_message: Status message.

    :return: Built `unverified request` response.
    """

    response = BotAPIUnverifiedRequestResponse(
        error_data=BotAPIUnverifiedRequestErrorData(status_message=status_message),
    )

    return asdict(response)
