"""Common responses for mocks."""

import uuid
from typing import Union

from starlette.responses import Response

from botx.models.requests import CommandResult, Notification
from botx.models.responses import PushResponse, PushResult


def generate_push_response(payload: Union[CommandResult, Notification]) -> Response:
    """Generate response as like new message from bot was pushed.

    Arguments:
        payload: pushed message.

    Returns:
        Response with sync_id for new message.
    """
    sync_id = payload.event_sync_id or uuid.uuid4()
    return Response(
        PushResponse(result=PushResult(sync_id=sync_id)).json(),
        media_type="application/json",
    )
