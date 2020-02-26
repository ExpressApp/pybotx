"""Implementation for BotX API clients."""

from uuid import UUID

import httpx
from httpx import Response
from loguru import logger

from botx.api_helpers import BotXAPI, RequestPayloadBuilder, is_api_error_code
from botx.exceptions import BotXAPIError
from botx.models.requests import (
    AddRemoveUsersPayload,
    StealthDisablePayload,
    StealthEnablePayload,
)
from botx.models.responses import PushResponse, TokenResponse
from botx.models.sending import MessagePayload, SendingCredentials, UpdatePayload
from botx.utils import LogsShapeBuilder

_HOST_SHOULD_BE_FILLED_ERROR = "Host should be filled in credentials"
_BOT_ID_SHOULD_BE_FILLED_ERROR = "Bot ID should be filled in credentials"
_TOKEN_SHOULD_BE_FILLED_ERROR = "Token should be filled in credentials"  # noqa: S105
_TEXT_OR_FILE_MISSED_ERROR = "text or file should present in payload"
_REQUEST_SCHEMAS = ("http", "https")
SECURE_SCHEME = "https"


class BaseClient:
    """Base class for implementing client for making requests to BotX API."""

    default_headers = {"content-type": "application/json"}

    def __init__(self, scheme: str = SECURE_SCHEME) -> None:
        """Init client with required params.

        Arguments:
            scheme: HTTP request scheme.
        """
        self.scheme = scheme

    @property
    def scheme(self) -> str:
        """HTTP request scheme for BotX API."""
        return self._scheme

    @scheme.setter  # noqa: WPS440
    def scheme(self, scheme: str) -> None:
        """HTTP request scheme for BotX API."""
        if scheme not in _REQUEST_SCHEMAS:
            raise ValueError("request scheme can be only http or https")
        self._scheme = scheme

    def _get_bearer_headers(self, token: str) -> dict:
        """Create authorization headers for BotX API v3 requests.

        Arguments:
            token: obtained token for bot.

        Return:
            Dict that will be used as headers.
        """
        return {"Authorization": f"Bearer {token}"}

    def _check_api_response(self, response: Response, error_message: str) -> None:
        """Check if response is errored, log it and raise exception.

        Arguments:
            response: response from BotX API.
            error_message: message that will be logged.
        """
        if is_api_error_code(response.status_code):
            logger.bind(
                botx_http_client=True,
                payload=LogsShapeBuilder.get_response_shape(response),
            ).error(error_message)
            raise BotXAPIError(error_message)


class AsyncClient(BaseClient):
    """Async client for making calls to BotX API."""

    def __init__(self, scheme: str = SECURE_SCHEME) -> None:
        """Init client to BotX API.

        Arguments:
            scheme: HTTP scheme.
        """
        super().__init__(scheme)

        self.http_client: httpx.AsyncClient = httpx.AsyncClient(
            headers=self.default_headers, http2=True
        )
        """HTTP client for requests."""

    async def obtain_token(self, host: str, bot_id: UUID, signature: str) -> str:
        """Send request to BotX API to obtain token for bot.

        Arguments:
            host: host for URL.
            bot_id: bot id which token should be obtained.
            signature: calculated signature for bot.

        Returns:
            Obtained token.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
        """
        logger.bind(
            botx_http_client=True,
            payload=LogsShapeBuilder.get_token_request_shape(host, bot_id, signature),
        ).debug("obtain token for requests")
        token_response = await self.http_client.get(
            BotXAPI.token(host=host, bot_id=bot_id, scheme=self.scheme),
            params=RequestPayloadBuilder.build_token_query_params(signature=signature),
        )
        self._check_api_response(token_response, "unable to obtain token from BotX API")

        parsed_response = TokenResponse.parse_obj(token_response.json())
        return parsed_response.result

    async def send_command_result(
        self, credentials: SendingCredentials, payload: MessagePayload
    ) -> UUID:
        """Send command result to BotX API using `sync_id` from credentials.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: command result that should be sent to BotX API.

        Returns:
            `UUID` of sent event if message was send as command result or `None` if
            message was sent as notification.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
            RuntimeError: raise if there was an error in payload configuration.
        """
        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        if not (payload.text or payload.file):
            raise RuntimeError(_TEXT_OR_FILE_MISSED_ERROR)

        command_result = RequestPayloadBuilder.build_command_result(
            credentials, payload
        )
        logger.bind(
            botx_http_client=True,
            payload=LogsShapeBuilder.get_command_result_shape(credentials, payload),
        ).debug("send command result to BotX API")
        command_response = await self.http_client.post(
            BotXAPI.command(host=credentials.host, scheme=self.scheme),
            data=command_result.json(by_alias=True),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(
            command_response, "unable to send command result to BotX API"
        )

        parsed_response = PushResponse.parse_obj(command_response.json())
        return parsed_response.result.sync_id

    async def send_notification(
        self, credentials: SendingCredentials, payload: MessagePayload
    ) -> None:
        """Send notification into chat or chats.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: command result that should be sent to BotX API.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
            RuntimeError: raise if there was an error in payload configuration.
        """
        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        if not (payload.text or payload.file):
            raise RuntimeError(_TEXT_OR_FILE_MISSED_ERROR)

        notification = RequestPayloadBuilder.build_notification(credentials, payload)
        logger.bind(
            botx_http_client=True,
            payload=LogsShapeBuilder.get_notification_shape(credentials, payload),
        ).debug("send notification to BotX API")
        notification_response = await self.http_client.post(
            BotXAPI.notification(host=credentials.host, scheme=self.scheme),
            data=notification.json(by_alias=True),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(
            notification_response, "unable to send notification to BotX API"
        )

    async def edit_event(
        self, credentials: SendingCredentials, update_payload: UpdatePayload
    ) -> None:
        """Edit event sent from bot.

        Arguments:
            credentials: credentials that are used for sending result.
            update_payload: update payload for message.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
        """
        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR

        edition = RequestPayloadBuilder.build_event_edition(credentials, update_payload)
        logger.bind(
            botx_http_client=True,
            payload=LogsShapeBuilder.get_edition_shape(credentials, update_payload),
        ).debug("update event in BotX API")
        update_event_response = await self.http_client.post(
            BotXAPI.edit_event(host=credentials.host, scheme=self.scheme),
            data=edition.json(by_alias=True, exclude_none=True),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(
            update_event_response, "unable to update event in BotX API"
        )

    async def stealth_enable(
        self, credentials: SendingCredentials, payload: StealthEnablePayload
    ) -> None:
        """Enable stealth mode.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: silent mode options.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
        """

        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        logger.bind(payload=payload.dict()).debug("Stealth mode enable")
        response = await self.http_client.post(
            BotXAPI.stealth_enable(host=credentials.host, scheme=self.scheme),
            data=payload.json(),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(response, "Unable to set stealth mode")

    async def stealth_disable(
        self, credentials: SendingCredentials, payload: StealthDisablePayload
    ) -> None:
        """Disable stealth mode.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: contains chat ID.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
        """

        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        logger.bind(payload=payload.dict()).debug("Stealth mode disable")
        response = await self.http_client.post(
            BotXAPI.stealth_disable(host=credentials.host, scheme=self.scheme),
            data=payload.json(),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(response, "Unable to unset stealth mode")

    async def add_users(
        self, credentials: SendingCredentials, payload: AddRemoveUsersPayload
    ) -> None:
        """Add users to chat.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: contains chat ID and users' huids.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
        """
        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        logger.bind(payload=payload.dict()).debug("add users to chat")
        response = await self.http_client.post(
            BotXAPI.add_user(host=credentials.host, scheme=self.scheme),
            data=payload.json(),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(response, "unable to add users to chat")

    async def remove_users(
        self, credentials: SendingCredentials, payload: AddRemoveUsersPayload
    ) -> None:
        """Remove users from chat.

        Arguments:
            credentials: credentials that are used for sending result.
            payload: contains chat ID and users' huids.

        Raises:
            BotXAPIError: raised if there was an error in calling BotX API.
            AssertionError: raised if there was an error in credentials configuration.
        """
        assert credentials.host, _HOST_SHOULD_BE_FILLED_ERROR
        assert credentials.token, _TOKEN_SHOULD_BE_FILLED_ERROR
        logger.bind(payload=payload.dict()).debug("remove users from chat")
        response = await self.http_client.post(
            BotXAPI.remove_user(host=credentials.host, scheme=self.scheme),
            data=payload.json(),
            headers=self._get_bearer_headers(token=credentials.token),
        )
        self._check_api_response(response, "unable to remove users from chat")


class Client(BaseClient):
    """Synchronous client for making calls to BotX API."""
