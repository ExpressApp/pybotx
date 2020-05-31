"""Endpoints for chats resource."""

from molten import Request, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.models.users import UserFromSearch
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.entities import create_test_user
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(ByHUID)
def get_by_huid(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information about user.
    """
    payload = ByHUID.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](
            result=create_test_user(user_huid=payload.user_huid),
        ),
    )


@bind_implementation_to_method(ByEmail)
def get_by_email(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information about user.
    """
    payload = ByEmail.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](result=create_test_user(email=payload.email)),
    )


@bind_implementation_to_method(ByLogin)
def get_by_login(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information about user.
    """
    payload = ByLogin.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](
            result=create_test_user(ad=(payload.ad_login, payload.ad_domain)),
        ),
    )
