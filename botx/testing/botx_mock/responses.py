"""Common responses for mocks."""

import uuid
from typing import Union

from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.types.push_response import PushResult


def generate_push_response(
    payload: Union[CommandResult, NotificationDirect]
) -> Response:
    """Generate response as like new message from bot was pushed.

    Arguments:
        payload: pushed message.

    Returns:
        Response with sync_id for new message.
    """
    sync_id = payload.event_sync_id or uuid.uuid4()
    return Response(
        APIResponse[PushResult](result=PushResult(sync_id=sync_id)).json(),
        media_type="application/json",
    )
