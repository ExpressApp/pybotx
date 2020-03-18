"""Definition for test client for bots."""

import uuid
from typing import Any, BinaryIO, Callable, List, Optional, TextIO, Tuple, Union

import httpx
from starlette import status
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.api_helpers import BotXAPI
from botx.bots import Bot
from botx.models import enums, events, files, receiving, requests, responses
from botx.models.enums import ChatTypes
from botx.models.requests import UpdatePayload

APIMessage = Union[
    requests.CommandResult,
    requests.Notification,
    requests.UpdatePayload,
    requests.StealthEnablePayload,
    requests.StealthDisablePayload,
    requests.AddRemoveUsersPayload,
]


class _BotXAPICallbacksFactory:
    """Factory for generating mocks for BotX API."""

    _error_response = JSONResponse(
        {"result": "API error"}, status_code=status.HTTP_400_BAD_REQUEST
    )

    def __init__(
        self, messages: List[APIMessage], generate_errored: bool = False
    ) -> None:
        """Init factory with required params.

        Arguments:
            messages: list of entities that will be sent from bot.
            generate_errored: generate endpoints that will return errored views.
        """
        self.messages = messages
        self.generate_errored = generate_errored

    def get_command_result_callback(self) -> Callable:
        """Generate callback for command result endpoint."""  # noqa: D202

        async def factory(request: Request) -> Response:
            command_result = requests.CommandResult.parse_obj(await request.json())
            self.messages.append(command_result)

            if self.generate_errored:
                return self._error_response

            return Response(
                responses.PushResponse(
                    result=responses.PushResult(sync_id=uuid.uuid4())
                ).json(),
                media_type="application/json",
            )

        return factory

    def get_notification_callback(self) -> Callable:
        """Generate callback for notification endpoint."""  # noqa: D202

        async def factory(request: Request) -> Response:
            notification = requests.Notification.parse_obj(await request.json())
            self.messages.append(notification)

            if self.generate_errored:
                return self._error_response

            return Response(
                responses.PushResponse(
                    result=responses.PushResult(sync_id=uuid.uuid4())
                ).json(),
                media_type="application/json",
            )

        return factory

    def get_token_callback(self) -> Callable:
        """Generate callback for token endpoint."""  # noqa: D202

        async def factory(_: Request) -> JSONResponse:
            if self.generate_errored:
                return self._error_response

            return JSONResponse(responses.TokenResponse(result="real token").dict())

        return factory

    def get_update_callback(self) -> Callable:
        """Generate callback for message update endpoint."""  # noqa: D202

        async def factory(request: Request) -> JSONResponse:
            update = UpdatePayload.parse_obj((await request.json())["payload"])
            self.messages.append(update)
            if self.generate_errored:
                return self._error_response

            return JSONResponse({})

        return factory

    def get_stealth_enable_callback(self) -> Callable:
        """Generate callback for stealth enable endpoint."""  # noqa: D202

        async def factory(request: Request) -> JSONResponse:
            payload = requests.StealthEnablePayload.parse_obj(await request.json())
            self.messages.append(payload)
            return JSONResponse(responses.StealthResponse().dict())

        return factory

    def get_stealth_disable_callback(self) -> Callable:
        """Generate callback for stealth disable endpoint."""  # noqa: D202

        async def factory(request: Request) -> JSONResponse:
            payload = requests.StealthDisablePayload.parse_obj(await request.json())
            self.messages.append(payload)
            return JSONResponse(responses.StealthResponse().dict())

        return factory

    def get_add_remove_user_callback(self) -> Callable:
        """Generate callback for add/remove user endpoints."""  # noqa: D202

        async def factory(request: Request) -> JSONResponse:
            payload = requests.AddRemoveUsersPayload.parse_obj(await request.json())
            self.messages.append(payload)
            return JSONResponse(responses.AddRemoveUserResponse().dict())

        return factory


def _botx_api_mock(
    messages: List[APIMessage], generate_errored: bool = False
) -> Starlette:
    """Get ASGI application for mock HTTP client for BotX API.

    Arguments:
        messages*: messages that stores entities sent to BotX API.
        generate_errored*: generate endpoints that will return errored views.

    Returns:
        Starlette mock application.
    """
    factory = _BotXAPICallbacksFactory(messages, generate_errored)
    app = Starlette()
    app.add_route(
        BotXAPI.command_endpoint.endpoint,
        factory.get_command_result_callback(),
        [BotXAPI.command_endpoint.method],
    )
    app.add_route(
        BotXAPI.notification_endpoint.endpoint,
        factory.get_notification_callback(),
        [BotXAPI.notification_endpoint.method],
    )
    app.add_route(
        BotXAPI.token_endpoint.endpoint,
        factory.get_token_callback(),
        [BotXAPI.token_endpoint.method],
    )
    app.add_route(
        BotXAPI.edit_event_endpoint.endpoint,
        factory.get_update_callback(),
        [BotXAPI.edit_event_endpoint.method],
    )
    app.add_route(
        BotXAPI.stealth_set_endpoint.endpoint,
        factory.get_stealth_enable_callback(),
        [BotXAPI.stealth_set_endpoint.method],
    )
    app.add_route(
        BotXAPI.stealth_disable_endpoint.endpoint,
        factory.get_stealth_disable_callback(),
        [BotXAPI.stealth_disable_endpoint.method],
    )
    app.add_route(
        BotXAPI.add_user_endpoint.endpoint,
        factory.get_add_remove_user_callback(),
        [BotXAPI.add_user_endpoint.method],
    )
    app.add_route(
        BotXAPI.remove_user_endpoint.endpoint,
        factory.get_add_remove_user_callback(),
        [BotXAPI.remove_user_endpoint.method],
    )
    return app


# There are a lot of properties and functions here, since message is a complex type
# that should be carefully validated.
# Properties are count as normal functions, so disable
# 1) too many methods (a lot of properties)
# 2) block variables overlap (setters are counted as replacement for functions)
class MessageBuilder:  # noqa: WPS214
    """Builder for command message for bot."""

    def __init__(
        self,
        body: str = "",
        bot_id: Optional[uuid.UUID] = None,
        user: Optional[receiving.User] = None,
    ) -> None:
        """Init builder with required params.

        Arguments:
            body: command body.
            bot_id: id of bot that will be autogenerated if not passed.
            user: user from which command was received.
        """
        self._user: receiving.User = user or self._default_user
        self._bot_id = bot_id or uuid.uuid4()
        self._body: str = ""
        self._is_system_command: bool = False
        self._command_data: dict = {}
        self._file: Optional[files.File] = None

        # checks for special invariants for events
        self._event_checkers = {
            events.SystemEvents.chat_created: self._check_chat_created_event,
            events.SystemEvents.file_transfer: self._check_file_transfer_event,
        }

        self.body = body

    @property
    def bot_id(self) -> uuid.UUID:
        """Id of bot."""
        return self._bot_id

    @bot_id.setter  # noqa: WPS440
    def bot_id(self, bot_id: uuid.UUID) -> None:
        """Id of bot."""
        self._bot_id = bot_id

    @property
    def body(self) -> str:
        """Message body."""
        return self._body

    @body.setter  # noqa: WPS440
    def body(self, body: str) -> None:
        """Message body."""
        self._check_system_command_properties(
            body, self._is_system_command, self._command_data
        )
        self._body = body

    @property
    def command_data(self) -> dict:
        """Additional command data."""
        return self._command_data

    @command_data.setter  # noqa: WPS440
    def command_data(self, command_data: dict) -> None:
        """Additional command data."""
        self._command_data = command_data

    @property
    def system_command(self) -> bool:
        """Is command a system event."""
        return self._is_system_command

    @system_command.setter  # noqa: WPS440
    def system_command(self, is_system_command: bool) -> None:
        """Is command a system event."""
        self._check_system_command_properties(
            self._body, is_system_command, self._command_data
        )
        self._is_system_command = is_system_command

    @property
    def file(self) -> Optional[files.File]:
        """File attached to message."""
        return self._file

    @file.setter  # noqa: WPS440
    def file(self, file: Optional[Union[files.File, BinaryIO, TextIO]]) -> None:
        """File that will be attached to message."""
        if isinstance(file, files.File) or file is None:
            self._file = file
        else:
            self._file = files.File.from_file(file, filename="temp.txt")
            self._file.file_name = file.name

    @property
    def user(self) -> receiving.User:
        """User from which message will be received."""
        return self._user

    @user.setter  # noqa: WPS440
    def user(self, user: receiving.User) -> None:
        """User from which message will be received."""
        self._user = user

    @property
    def message(self) -> receiving.IncomingMessage:
        """Message that was built by builder."""
        command_type = (
            enums.CommandTypes.system
            if self.system_command
            else enums.CommandTypes.user
        )
        command = receiving.Command(
            body=self.body, command_type=command_type, data=self.command_data
        )
        return receiving.IncomingMessage(
            sync_id=uuid.uuid4(),
            command=command,
            file=self.file,
            bot_id=self.bot_id,
            user=self.user,
        )

    @property
    def _default_user(self) -> receiving.User:
        """User that will be used in __init__ as fallback."""
        return receiving.User(
            user_huid=uuid.uuid4(),
            group_chat_id=uuid.uuid4(),
            chat_type=ChatTypes.chat,
            ad_login="test_user",
            ad_domain="example.com",
            username="Test User",
            is_admin=True,
            is_creator=True,
            host="cts.example.com",
        )

    def _check_system_command_properties(
        self, body: str, is_system_command: bool, command_data: dict
    ) -> None:
        """Check that system event message is valid.

        Arguments:
            body: message body.
            is_system_command: flag that command is system event.
            command_data: additional data that will be included into message and should
                be validated.
        """
        if is_system_command:
            event = events.SystemEvents(body)  # check that is real system event
            event_shape = events.EVENTS_SHAPE_MAP.get(event)
            if event_shape:
                event_shape.parse_obj(command_data)  # check event data
            self._event_checkers[event]()

    def _check_chat_created_event(self) -> None:
        """Check invariants for `system:chat_created` event."""
        assert (
            not self.user.user_huid
        ), "A user in system:chat_created can not have user_huid"
        assert (
            not self.user.ad_login
        ), "A user in system:chat_created can not have ad_login"
        assert (
            not self.user.ad_domain
        ), "A user in system:chat_created can not have ad_domain"
        assert (
            not self.user.username
        ), "A user in system:chat_created can not have username"

    def _check_file_transfer_event(self) -> None:
        """Check invariants for `file_transfer` event."""
        assert self.file, "file_transfer event should have attached file"


class TestClient:  # noqa: WPS214
    """Test client for testing bots."""

    def __init__(self, bot: Bot, generate_error_api: bool = False) -> None:
        """Init client with required params.

        Arguments:
            bot: bot that should be tested.
            generate_error_api: mocked BotX API will return errored responses.
        """
        self.bot: Bot = bot
        """Bot that will be patched for tests."""
        self._original_http_client = bot.client.http_client
        self._messages: List[APIMessage] = []
        self._generate_error_api = generate_error_api

    @property
    def generate_error_api(self) -> bool:
        """Regenerate BotX API mock."""
        return self._generate_error_api

    @generate_error_api.setter
    def generate_error_api(self, generate_errored: bool) -> None:
        """Regenerate BotX API mock."""
        self._generate_error_api = generate_errored
        self.bot.client.http_client = httpx.AsyncClient(
            app=_botx_api_mock(self._messages, self.generate_error_api)
        )

    def __enter__(self) -> "TestClient":
        """Mock original HTTP client."""
        self.bot.client.http_client = httpx.AsyncClient(
            app=_botx_api_mock(self._messages, self.generate_error_api)
        )

        return self

    def __exit__(self, *_: Any) -> None:
        """Restore original HTTP client and clear storage."""
        self.bot.client.http_client = self._original_http_client
        self._messages = []

    async def send_command(
        self, message: receiving.IncomingMessage, sync: bool = True
    ) -> None:
        """Send command message to bot.

        Arguments:
            message: message with command for bot.
            sync: if is `True` then wait while command is full executed.
        """
        await self.bot.execute_command(message.dict())

        if sync:
            await self.bot.shutdown()

    @property
    def messages(self) -> Tuple[APIMessage, ...]:
        """Return all entities that were sent by bot.

        Returns:
            Sequence of messages that were sent from bot.
        """
        return tuple(message.copy(deep=True) for message in self._messages)

    @property
    def command_results(self) -> Tuple[requests.CommandResult, ...]:
        """Return all command results that were sent by bot.

        Returns:
            Sequence of command results that were sent from bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, requests.CommandResult)
        )

    @property
    def notifications(self) -> Tuple[requests.Notification, ...]:
        """Return all notifications that were sent by bot.

        Returns:
            Sequence of notifications that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, requests.Notification)
        )

    @property
    def message_updates(self) -> Tuple[requests.UpdatePayload, ...]:
        """Return all updates that were sent by bot.

        Returns:
            Sequence of updates that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, requests.UpdatePayload)
        )
