from typing import Any
from uuid import UUID

from pybotx.domain.constants import BOT_API_VERSION

class UnknownBotAccountError(Exception):
    def __init__(self, bot_id: UUID) -> None:
        self.bot_id = bot_id
        self.message = f"No bot account with bot_id: `{bot_id!s}`"
        super().__init__(self.message)


class BotXMethodCallbackNotFoundError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = (
            f"Callback `{sync_id}` doesn't exist or already waited or timed out"
        )
        super().__init__(self.message)


class BotShuttingDownError(Exception):
    def __init__(self, context: Any) -> None:
        self.context = context
        self.message = f"Bot is shutting down: {context}"
        super().__init__(self.message)


class AnswerDestinationLookupError(Exception):
    def __init__(self) -> None:
        self.message = "No IncomingMessage received. Use `Bot.send` instead"
        super().__init__(self.message)


class RequestHeadersNotProvidedError(Exception):
    def __init__(self, *args: Any) -> None:
        reason = "To verify the request you should provide headers."
        message = args[0] if args else reason
        super().__init__(message)


class UnverifiedRequestError(Exception):
    """The authorization header is missing or the token is invalid."""


class JwtEncodingError(Exception):
    """JWT encoding failed."""


class BotXValidationError(Exception):
    """Base class for validation errors raised by pybotx."""


class BotCommandValidationError(BotXValidationError):
    """Incoming bot command payload is invalid."""


class SyncSmartAppEventValidationError(BotXValidationError):
    """Incoming sync smartapp event payload is invalid."""


class StatusRequestValidationError(BotXValidationError):
    """Status request payload is invalid."""


class InvalidCommandNameError(BotXValidationError):
    """Command name doesn't match required format."""


class HandlerAlreadyRegisteredError(BotXValidationError):
    """Handler for the given key is already registered."""


class CommandDescriptionRequiredError(BotXValidationError):
    """Visible command requires a description."""


class InvalidMarkupError(BotXValidationError):
    """Invalid message markup configuration."""


class InvalidWidgetPayloadError(BotXValidationError):
    """Invalid widget payload or state."""


class InvalidBotCommandLinkError(BotXValidationError):
    """Invalid bot command link parameters."""


class InvalidCtsUrlError(BotXValidationError):
    """Failed to parse host from CTS URL."""


class InvalidAvatarDataError(BotXValidationError):
    """Avatar must be a valid data URL (RFC2397)."""


class NotificationBodyTooLongError(BotXValidationError):
    """Notification body exceeds maximum allowed length."""


class InvalidStickerImageError(BotXValidationError):
    """Sticker image validation failed."""


class StickerImageTooLargeError(BotXValidationError):
    """Sticker image exceeds maximum allowed size."""


class InvalidWebhookPayloadError(BotXValidationError):
    """Webhook payload must be a JSON object."""


class TestkitConfigurationError(BotXValidationError):
    """Testkit configuration is invalid."""


class TransportError(Exception):
    """Network/transport-level error."""


class BaseClientError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    @classmethod
    def from_response(
        cls,
        response: Any,
        comment: str | None = None,
    ) -> "BaseClientError":
        method = response.request.method
        url = response.request.url
        status_code = response.status_code
        content = response.content

        message = (
            f"{method} {url}\n"
            f"failed with code {status_code} and payload:\n"
            f"{content!r}"
        )

        if comment is not None:
            message = f"{message}\n\nComment: {comment}"

        return cls(message)

    @classmethod
    def from_callback(
        cls,
        callback: Any,
        comment: str | None = None,
    ) -> "BaseClientError":
        message = (
            f"BotX method call with sync_id `{callback.sync_id!s}` "
            f"failed with: {callback}"
        )

        if comment is not None:
            message = f"{message}\n\nComment: {comment}"

        return cls(message)


class InvalidBotAccountError(BaseClientError):
    """Bot account is invalid or unauthorized."""


class ChatNotFoundError(BaseClientError):
    """Chat not found."""


class PermissionDeniedError(BaseClientError):
    """Access denied."""


class RateLimitReachedError(BaseClientError):
    """Rate limit exceeded."""


class CallbackNotReceivedError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = f"Callback for sync_id `{sync_id}` hasn't been received"
        super().__init__(self.message)


class SyncSmartAppEventHandlerNotFoundError(BaseClientError):
    """Handler for synchronous smartapp event not found."""


class UnsupportedBotAPIVersionError(Exception):
    def __init__(self, version: int) -> None:
        self.version = version
        self.message = (
            f"Unsupported Bot API version: `{version}`, expected `{BOT_API_VERSION}`"
        )
        super().__init__(self.message)


class UnknownSystemEventError(Exception):
    def __init__(self, type_name: str) -> None:
        self.type_name = type_name
        self.message = f"Unknown system event: `{type_name}`"
        super().__init__(self.message)
