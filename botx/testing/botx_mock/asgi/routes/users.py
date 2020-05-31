"""Endpoints for chats resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.models.users import UserFromSearch
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.entities import create_test_user


@bind_implementation_to_method(ByHUID)
async def get_by_huid(request: Request) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByHUID.parse_obj(request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](
            result=create_test_user(user_huid=payload.user_huid),
        ),
    )


@bind_implementation_to_method(ByEmail)
async def get_by_email(request: Request) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByEmail.parse_obj(request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](result=create_test_user(email=payload.email)),
    )


@bind_implementation_to_method(ByLogin)
async def get_by_login(request: Request) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByLogin.parse_obj(request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](
            result=create_test_user(ad=(payload.ad_login, payload.ad_domain)),
        ),
    )
