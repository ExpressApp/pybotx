"""Endpoints for chats resource."""
import uuid
from typing import Optional, Tuple

from molten import Request, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.clients.types.users import UserFromSearch
from botx.testing.botx_mock.wsgi.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


def _get_test_user(
    *,
    user_huid: Optional[uuid.UUID] = None,
    email: Optional[str] = None,
    ad: Optional[Tuple[str, str]] = None,
) -> UserFromSearch:
    return UserFromSearch(
        user_huid=user_huid or uuid.uuid4(),
        ad_login=ad[0] if ad else "ad_login",
        ad_domain=ad[1] if ad else "ad_domain",
        name="test user",
        company="test company",
        company_position="test position",
        department="test department",
        emails=[email or "test@example.com"],
    )


@bind_implementation_to_method(ByHUID)
def get_by_huid(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByHUID.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](result=_get_test_user(user_huid=payload.user_huid)),
    )


@bind_implementation_to_method(ByEmail)
def get_by_email(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByEmail.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](result=_get_test_user(email=payload.email)),
    )


@bind_implementation_to_method(ByLogin)
def get_by_login(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information about user.
    """
    payload = ByLogin.parse_obj(dict(request.params))
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[UserFromSearch](
            result=_get_test_user(ad=(payload.ad_login, payload.ad_domain))
        ),
    )
