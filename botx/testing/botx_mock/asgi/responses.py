"""Common responses for mocks."""

import uuid
from typing import Any, Union

from pydantic import BaseModel
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.types.response_results import PushResult


class PydanticResponse(Response):
    """Custom response to encode pydantic model from route."""

    def __init__(
        self,
        model: BaseModel,
        status_code: int = 200,
        media_type: str = "application/json",
        **kwargs: Any,
    ) -> None:
        """Init custom response.

        Arguments:
            model: pydantic model that should be encoded.
            status_code: response HTTP status code.
            media_type: content type of response.
            kwargs: other arguments to response constructor from starlette.
        """
        super().__init__(
            model.json(by_alias=True), status_code, media_type=media_type, **kwargs,
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
