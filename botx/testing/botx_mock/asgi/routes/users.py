"""Endpoints for chats resource."""
import uuid
from typing import Optional, Tuple

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.clients.types.users import UserFromSearch
from botx.testing.botx_mock.asgi.binders import bind_implementation_to_method
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse


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
        APIResponse[UserFromSearch](result=_get_test_user(user_huid=payload.user_huid)),
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
        APIResponse[UserFromSearch](result=_get_test_user(email=payload.email)),
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
            result=_get_test_user(ad=(payload.ad_login, payload.ad_domain))
        ),
    )
