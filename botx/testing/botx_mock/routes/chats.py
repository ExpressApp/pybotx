"""Endpoints for chats resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.models.requests import (
    AddRemoveUsersPayload,
    StealthDisablePayload,
    StealthEnablePayload,
)
from botx.models.responses import AddRemoveUserResponse, StealthResponse
from botx.testing.botx_mock.messages import add_request_to_collection


async def post_add_user(request: Request) -> Response:
    """Handle adding of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = AddRemoveUsersPayload.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(AddRemoveUserResponse().dict())


async def post_remove_user(request: Request) -> Response:
    """Handle removing of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of removing.
    """
    payload = AddRemoveUsersPayload.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(AddRemoveUserResponse().dict())


async def post_stealth_set(request: Request) -> Response:
    """Handle stealth enabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of enabling stealth.
    """
    payload = StealthEnablePayload.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(StealthResponse().dict())


async def post_stealth_disable(request: Request) -> Response:
    """Handle stealth disabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of disabling stealth.
    """
    payload = StealthDisablePayload.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(StealthResponse().dict())
