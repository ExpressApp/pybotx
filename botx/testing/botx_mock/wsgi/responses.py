"""Common responses for mocks."""

import uuid
from typing import Any, Dict, Optional, Union

from molten import HTTP_200, Response
from pydantic import BaseModel

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v4.notifications.internal_bot_notification import (
    InternalBotNotification,
)
from botx.clients.types.response_results import (
    InternalBotNotificationResult,
    PushResult,
)


class PydanticResponse(Response):
    """Custom response to encode pydantic model from route."""

    def __init__(
        self,
        model: BaseModel,
        status_code: str = HTTP_200,
        headers: Optional[Dict[Any, Any]] = None,
    ) -> None:
        """Init custom response.

        Arguments:
            model: pydantic model that should be encoded.
            status_code: response HTTP status code.
            headers: headers for response.
        """
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        super().__init__(
            status_code,
            headers,
            model.json(by_alias=True),
        )


def generate_push_response(
    payload: Union[CommandResult, NotificationDirect],
) -> Response:
    """Generate response as like new message from bot was pushed.

    Arguments:
        payload: pushed message.

    Returns:
        Response with sync_id for new message.
    """
    sync_id = payload.event_sync_id or uuid.uuid4()
    return PydanticResponse(
        APIResponse[PushResult](result=PushResult(sync_id=sync_id)),
    )


def generate_internal_bot_notification_response(
    payload: InternalBotNotification,
) -> Response:
    """Generate response as like internal bot notification was sent.

    Arguments:
        payload: sent notification.

    Returns:
        Response with sync_id for new message.
    """
    sync_id = uuid.uuid4()
    return PydanticResponse(
        APIResponse[InternalBotNotificationResult](
            result=InternalBotNotificationResult(sync_id=sync_id),
        ),
    )
