"""Endpoints for chats resource."""
import uuid

from molten import Request, RequestData, Response, Settings

from botx import ChatTypes, UserKinds
from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.create import Create
from botx.clients.methods.v3.chats.info import Info
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.clients.types.chats import ChatFromSearch
from botx.clients.types.response_results import ChatCreatedResult
from botx.models.events import UserInChatCreated
from botx.testing.botx_mock.wsgi.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(Info)
def get_info(request: Request, settings: Settings) -> Response:
    """Handle retrieving information of chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information of chat.
    """
    payload = Info.parse_obj(request.params)
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[ChatFromSearch](
            result=ChatFromSearch(
                name="chat name",
                chat_type=ChatTypes.group_chat,
                creator=uuid.uuid4(),
                group_chat_id=payload.group_chat_id,
                members=[
                    UserInChatCreated(
                        huid=uuid.uuid4(),
                        user_kind=UserKinds.user,
                        name="user name",
                        admin=True,
                    ),
                ],
            ),
        ),
    )


@bind_implementation_to_method(AddUser)
def post_add_user(request_data: RequestData, settings: Settings) -> Response:
    """Handle adding of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = AddUser.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(RemoveUser)
def post_remove_user(request_data: RequestData, settings: Settings) -> Response:
    """Handle removing of user to chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of removing.
    """
    payload = RemoveUser.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(StealthSet)
def post_stealth_set(request_data: RequestData, settings: Settings) -> Response:
    """Handle stealth enabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of enabling stealth.
    """
    payload = StealthSet.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(StealthDisable)
def post_stealth_disable(request_data: RequestData, settings: Settings) -> Response:
    """Handle stealth disabling in chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of disabling stealth.
    """
    payload = StealthDisable.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[bool](result=True))


@bind_implementation_to_method(Create)
def post_create(request_data: RequestData, settings: Settings) -> Response:
    """Handle creation of new chat request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of creation.
    """
    payload = Create.parse_obj(request_data)
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[ChatCreatedResult](result=ChatCreatedResult(chat_id=uuid.uuid4())),
    )
