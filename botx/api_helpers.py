"""Definition of useful functions for BotX API related stuff."""

from typing import Any, cast
from uuid import UUID

from httpx import StatusCode

from botx.models.requests import (
    CommandResult,
    EventEdition,
    Notification,
    ResultOptions,
    ResultPayload,
    UpdatePayload,
)
from botx.models.sending import (
    MessagePayload,
    SendingCredentials,
    UpdatePayload as SendingUpdatePayload,
)


class BotXEndpoint:
    """Definition of BotX API endpoint."""

    def __init__(self, method: str, endpoint: str) -> None:
        """Init endpoint with required params.

        Arguments:
            method: HTTP method that is used for endpoint.
            endpoint: relative oath to endpoint from host.
        """
        self.method = method
        self.endpoint = endpoint


_URL_TEMPLATE = "{scheme}://{host}{endpoint}"
HTTPS_SCHEME = "https"


class BotXAPI:
    """Builder for different BotX API endpoints."""

    token_endpoint = BotXEndpoint(
        method="GET", endpoint="/api/v2/botx/bots/{bot_id}/token"
    )
    command_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/command/callback"
    )
    notification_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/notification/callback"
    )
    edit_event_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/events/edit_event"
    )
    add_user_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/chats/add_user"
    )
    remove_user_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/chats/remove_user"
    )
    stealth_set_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/chats/stealth_set"
    )
    stealth_disable_endpoint = BotXEndpoint(
        method="POST", endpoint="/api/v3/botx/chats/stealth_disable"
    )

    @classmethod
    def token(
        cls, host: str, scheme: str = HTTPS_SCHEME, **endpoint_params: Any
    ) -> str:
        """Build token URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.
            endpoint_params: additional params for URL.

        Returns:
            URL for token endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme,
            host=host,
            endpoint=cls.token_endpoint.endpoint.format(**endpoint_params),
        )

    @classmethod
    def command(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build command result URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for command result endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.command_endpoint.endpoint
        )

    @classmethod
    def notification(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build notification URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for notification endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.notification_endpoint.endpoint
        )

    @classmethod
    def edit_event(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build edit event URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for edit event endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.edit_event_endpoint.endpoint
        )

    @classmethod
    def stealth_enable(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build stealth enable URL

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for stealth enable endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.stealth_set_endpoint.endpoint
        )

    @classmethod
    def stealth_disable(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build stealth disable URL

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for stealth disable endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.stealth_disable_endpoint.endpoint
        )

    @classmethod
    def add_user(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build add user URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for add user endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.add_user_endpoint.endpoint
        )

    @classmethod
    def remove_user(cls, host: str, scheme: str = HTTPS_SCHEME) -> str:
        """Build remove user URL.

        Arguments:
            host: host for URL.
            scheme: HTTP URL schema.

        Returns:
            URL for add user endpoint for BotX API.
        """
        return _URL_TEMPLATE.format(
            scheme=scheme, host=host, endpoint=cls.remove_user_endpoint.endpoint
        )


def is_api_error_code(code: int) -> bool:
    """Check that status code returned from BotX API is a HTTP error code.

    Arguments:
        code: HTTP status code returned from BotX API.

    Returns:
        A result of check.
    """
    return StatusCode.is_client_error(code) or StatusCode.is_server_error(code)


class RequestPayloadBuilder:
    """Builder for requests payload."""

    @classmethod
    def build_token_query_params(cls, signature: str) -> dict:
        """Create query params for token request.

        Arguments:
            signature: calculated signature for obtaining token for bot.

        Returns:
            A dictionary that will be used in token URL.
        """
        return {"signature": signature}

    @classmethod
    def build_command_result(
        cls, credentials: SendingCredentials, payload: MessagePayload
    ) -> CommandResult:
        """Build command result entity.

        Arguments:
            credentials: message credentials for generated command result.
            payload: message payload that is used for generation entity payload.

        Returns:
            Command result payload for API.
        """
        credentials.bot_id = cast(UUID, credentials.bot_id)

        return CommandResult(
            bot_id=credentials.bot_id,
            sync_id=cast(UUID, credentials.sync_id),
            command_result=cls._build_result_payload(payload),
            recipients=payload.options.recipients,
            file=payload.file,
            opts=ResultOptions(notification_opts=payload.options.notifications),
        )

    @classmethod
    def build_notification(
        cls, credentials: SendingCredentials, payload: MessagePayload
    ) -> Notification:
        """Build notification entity.

        Arguments:
            credentials: message credentials for generated notification.
            payload: message payload that is used for generation entity payload.

        Returns:
            A notification payload for API.
        """
        credentials.bot_id = cast(UUID, credentials.bot_id)

        return Notification(
            bot_id=credentials.bot_id,
            group_chat_ids=credentials.chat_ids,
            notification=cls._build_result_payload(payload),
            recipients=payload.options.recipients,
            file=payload.file,
            opts=ResultOptions(notification_opts=payload.options.notifications),
        )

    @classmethod
    def build_event_edition(
        cls, credentials: SendingCredentials, payload: SendingUpdatePayload
    ) -> EventEdition:
        """Build event edition entity.

        Arguments:
            credentials: credentials for message that will be send.
            payload: new message payload.

        Returns:
            A edit event payload for API.
        """
        credentials.sync_id = cast(UUID, credentials.sync_id)

        return EventEdition(
            sync_id=credentials.sync_id,
            payload=UpdatePayload(
                body=payload.text,
                keyboard=payload.keyboard,
                bubble=payload.bubbles,
                mentions=payload.mentions,
            ),
        )

    @classmethod
    def _build_result_payload(cls, payload: MessagePayload) -> ResultPayload:
        """Build payload for command result or notification.

        Arguments:
            payload: message payload that is used for generation entity payload.

        Returns:
            A common payload command result or notification for API.
        """
        return ResultPayload(
            body=payload.text,
            bubble=payload.markup.bubbles,
            keyboard=payload.markup.keyboard,
            mentions=payload.options.mentions,
        )
