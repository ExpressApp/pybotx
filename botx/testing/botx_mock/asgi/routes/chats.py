"""Endpoints for chats resource."""
import uuid

from starlette import requests, responses

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.chats import (
    add_admin_role,
    add_user,
    create,
    info,
    remove_user,
    stealth_disable,
    stealth_set,
)
from botx.clients.types.response_results import ChatCreatedResult
from botx.models import chats, enums, users
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(info.Info)
async def get_info(request: requests.Request) -> responses.Response:
    """Handle retrieving information of chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information of chat.
    """
    payload = info.Info.parse_obj(request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[chats.ChatFromSearch](
            result=chats.ChatFromSearch(
                name="chat name",
                chat_type=enums.ChatTypes.group_chat,
                creator=uuid.uuid4(),
                group_chat_id=payload.group_chat_id,
                members=[
                    users.UserFromChatSearch(
                        user_huid=uuid.uuid4(),
                        user_kind=enums.UserKinds.user,
                        admin=True,
                    ),
                ],
            ),
        ),
    )


@bind_implementation_to_method(add_user.AddUser)
async def post_add_user(request: requests.Request) -> responses.Response:
    """Handle adding of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = add_user.AddUser.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(remove_user.RemoveUser)
async def post_remove_user(request: requests.Request) -> responses.Response:
    """Handle removing of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of removing.
    """
    payload = remove_user.RemoveUser.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(stealth_set.StealthSet)
async def post_stealth_set(request: requests.Request) -> responses.Response:
    """Handle stealth enabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of enabling stealth.
    """
    payload = stealth_set.StealthSet.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(stealth_disable.StealthDisable)
async def post_stealth_disable(request: requests.Request) -> responses.Response:
    """Handle stealth disabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of disabling stealth.
    """
    payload = stealth_disable.StealthDisable.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(create.Create)
async def post_create(request: requests.Request) -> responses.Response:
    """Handle creation of new chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of creation.
    """
    payload = create.Create.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[ChatCreatedResult](result=ChatCreatedResult(chat_id=uuid.uuid4())),
    )


@bind_implementation_to_method(add_admin_role.AddAdminRole)
async def post_add_admin_role(request: requests.Request) -> responses.Response:
    """Handle promoting users to admins request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = add_admin_role.AddAdminRole.parse_obj(await request.json())
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[bool](result=True))
