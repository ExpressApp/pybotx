"""Endpoints for chats resource."""
import uuid
from datetime import datetime as dt

from molten import Request, RequestData, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.chats import (
    add_admin_role,
    add_user,
    chat_list,
    create,
    info,
    remove_user,
    stealth_disable,
    stealth_set,
)
from botx.clients.types.response_results import ChatCreatedResult
from botx.models import chats, enums, users
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(info.Info)
def get_info(request: Request, settings: Settings) -> Response:
    """Handle retrieving information of chat request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information of chat.
    """
    payload = info.Info.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    inserted_ad = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
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
                inserted_at=inserted_ad,
            ),
        ),
    )


@bind_implementation_to_method(chat_list.ChatList)
def get_bot_chats(request: Request, settings: Settings) -> Response:
    """Return list of bot chats.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
         List of bot chats.
    """
    payload = chat_list.ChatList.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    updated_at = dt.fromisoformat("2019-09-29T10:30:48.358586+00:00")
    return PydanticResponse(
        APIResponse[chats.BotChatList](
            result=chats.BotChatList(
                __root__=[
                    chats.BotChatFromList(
                        name="chat name",
                        description="test",
                        chat_type=enums.ChatTypes.group_chat,
                        group_chat_id=uuid.uuid4(),
                        members=[uuid.uuid4()],
                        inserted_at=inserted_at,
                        updated_at=updated_at,
                    ),
                ],
            ),
        ),
    )


@bind_implementation_to_method(add_user.AddUser)
def post_add_user(request_data: RequestData, settings: Settings) -> Response:
    """Handle adding of user to chat request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of adding.
    """
    payload = add_user.AddUser.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(remove_user.RemoveUser)
def post_remove_user(request_data: RequestData, settings: Settings) -> Response:
    """Handle removing of user to chat request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of removing.
    """
    payload = remove_user.RemoveUser.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(stealth_set.StealthSet)
def post_stealth_set(request_data: RequestData, settings: Settings) -> Response:
    """Handle stealth enabling in chat request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of enabling stealth.
    """
    payload = stealth_set.StealthSet.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(stealth_disable.StealthDisable)
def post_stealth_disable(request_data: RequestData, settings: Settings) -> Response:
    """Handle stealth disabling in chat request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of disabling stealth.
    """
    payload = stealth_disable.StealthDisable.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(create.Create)
def post_create(request_data: RequestData, settings: Settings) -> Response:
    """Handle creation of new chat request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of creation.
    """
    payload = create.Create.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[ChatCreatedResult](result=ChatCreatedResult(chat_id=uuid.uuid4())),
    )


@bind_implementation_to_method(add_admin_role.AddAdminRole)
def post_add_admin_role(request_data: RequestData, settings: Settings) -> Response:
    """Handle promoting users to admins request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of adding.
    """
    payload = add_admin_role.AddAdminRole.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))
