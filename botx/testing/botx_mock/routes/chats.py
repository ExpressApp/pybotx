"""Endpoints for chats resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.messages import add_request_to_collection


@bind_implementation_to_method(AddUser)
async def post_add_user(request: Request) -> Response:
    """Handle adding of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = AddUser.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(APIResponse[bool](result=True).dict())


@bind_implementation_to_method(RemoveUser)
async def post_remove_user(request: Request) -> Response:
    """Handle removing of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of removing.
    """
    payload = RemoveUser.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(APIResponse[bool](result=True).dict())


@bind_implementation_to_method(StealthSet)
async def post_stealth_set(request: Request) -> Response:
    """Handle stealth enabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of enabling stealth.
    """
    payload = StealthSet.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(APIResponse[bool](result=True).dict())


@bind_implementation_to_method(StealthDisable)
async def post_stealth_disable(request: Request) -> Response:
    """Handle stealth disabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of disabling stealth.
    """
    payload = StealthDisable.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return JSONResponse(APIResponse[bool](result=True).dict())
