from pybotx.domain.errors import UnknownSystemEventError, UnsupportedBotAPIVersionError
from pybotx.presentation.api.responses.bot_disabled import (
    BotAPIBotDisabledErrorData,
    BotAPIBotDisabledResponse,
    build_bot_disabled_response,
)
from pybotx.presentation.api.responses.command_accepted import build_command_accepted_response
from pybotx.presentation.api.responses.unverified_request import (
    BotAPIUnverifiedRequestErrorData,
    BotAPIUnverifiedRequestResponse,
    build_unverified_request_response,
)
from pybotx.domain.auth import BotXAuthVersion
from pybotx.container import BotXContainer, build_default_config, build_bot
from pybotx.application.bot import Bot
from pybotx.domain.ports.callback_repo import CallbackRepoProto
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort
from pybotx.domain.ports.attachment_factory import AttachmentFactoryPort
from pybotx.domain.bot_links import build_bot_command_link
from pybotx.domain.errors import (
    AnswerDestinationLookupError,
    BotShuttingDownError,
    BotXMethodCallbackNotFoundError,
    RequestHeadersNotProvidedError,
    UnknownBotAccountError,
    UnverifiedRequestError,
)
from pybotx.domain.errors import (
    BotCommandValidationError,
    BotXValidationError,
    CommandDescriptionRequiredError,
    HandlerAlreadyRegisteredError,
    InvalidAvatarDataError,
    InvalidBotCommandLinkError,
    InvalidCommandNameError,
    InvalidCtsUrlError,
    InvalidMarkupError,
    InvalidWidgetPayloadError,
    InvalidStickerImageError,
    InvalidWebhookPayloadError,
    JwtEncodingError,
    NotificationBodyTooLongError,
    StatusRequestValidationError,
    StickerImageTooLargeError,
    SyncSmartAppEventValidationError,
    TestkitConfigurationError,
)
from pybotx.application.handler import (
    IncomingMessageHandlerFunc,
    Middleware,
    SyncSmartAppEventHandlerFunc,
)
from pybotx.application.handler_collector import HandlerCollector
from pybotx.application.lifespan import lifespan_wrapper
from pybotx.application.bot_facets.widgets import MultiWidgetSendResult
from pybotx.infrastructure.client.exceptions.callbacks import (
    BotXMethodFailedCallbackReceivedError,
)
from pybotx.domain.errors import CallbackNotReceivedError
from pybotx.infrastructure.client.exceptions.chats import (
    CantUpdatePersonalChatError,
    ChatCreationError,
    ChatCreationProhibitedError,
    ChatLinkCreationError,
    ChatLinkCreationProhibitedError,
    InvalidUsersListError,
    ThreadAlreadyExistsError,
    ThreadCreationError,
    ThreadCreationProhibitedError,
)
from pybotx.domain.errors import (
    ChatNotFoundError,
    InvalidBotAccountError,
    PermissionDeniedError,
    RateLimitReachedError,
    TransportError,
)
from pybotx.infrastructure.client.exceptions.event import EventNotFoundError
from pybotx.infrastructure.client.exceptions.files import FileDeletedError, FileMetadataNotFound
from pybotx.infrastructure.client.exceptions.http import (
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from pybotx.infrastructure.client.exceptions.message import MessageNotFoundError
from pybotx.infrastructure.client.exceptions.notifications import (
    BotIsNotChatMemberError,
    FinalRecipientsListEmptyError,
    StealthModeDisabledError,
)
from pybotx.infrastructure.client.exceptions.users import UserNotFoundError
from pybotx.domain.errors import SyncSmartAppEventHandlerNotFoundError
from pybotx.infrastructure.aiohttp_client import AioHttpClientAdapter
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory
from pybotx.infrastructure.widget_state_store import (
    InMemoryWidgetStateStore,
    JsonWidgetStateSerializer,
    PickleWidgetStateSerializer,
    RedisWidgetStateStore,
    WidgetStateSerializer,
)
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestAuroraParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.infrastructure.client.stickers_api.exceptions import (
    InvalidEmojiError,
    InvalidImageError,
    StickerPackOrStickerNotFoundError,
)
from pybotx.domain.logger import logger
from pybotx.domain.ports.logger import LoggerPort
from pybotx.domain.models.async_files import Document, File, Image, Video, Voice
from pybotx.domain.models.attachments import (
    AttachmentDocument,
    AttachmentImage,
    AttachmentVideo,
    AttachmentVoice,
    OutgoingAttachment,
)
from pybotx.domain.models.bot_account import BotAccount, BotAccountWithSecret
from pybotx.domain.models.bot_catalog import BotsListItem
from pybotx.domain.models.bot_sender import BotSender
from pybotx.domain.models.chats import (
    Chat,
    ChatInfo,
    ChatInfoMember,
    ChatLink,
    ChatListItem,
)
from pybotx.domain.models.enums import (
    AttachmentTypes,
    ChatLinkTypes,
    ChatTypes,
    ClientPlatforms,
    ConferenceLinkTypes,
    MentionTypes,
    SmartappManifestWebLayoutChoices,
    SyncSourceTypes,
    UserKinds,
)
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.forward import Forward
from pybotx.domain.models.message.incoming_message import (
    IncomingMessage,
    UserDevice,
    UserSender,
)
from pybotx.domain.models.message.markup import (
    BubbleMarkup,
    Button,
    ButtonRow,
    ButtonTextAlign,
    KeyboardMarkup,
)
from pybotx.domain.models.message.bulk_results import (
    BulkEditItemResult,
    BulkEditResult,
    BulkReplyItemResult,
    BulkReplyResult,
    BulkSendItemResult,
    BulkSendResult,
)
from pybotx.domain.models.message.mentions import (
    Mention,
    MentionAll,
    MentionBuilder,
    MentionChannel,
    MentionChat,
    MentionContact,
    MentionList,
    MentionUser,
)
from pybotx.domain.text_builder import MentionComposer, TextBuilder
from pybotx.domain.models.message.message_status import MessageStatus
from pybotx.domain.models.message.message_options import MessageOptions, NotificationOptions
from pybotx.domain.models.message.outgoing_message import OutgoingMessage
from pybotx.domain.message_builder import (
    EditMessageBuilder,
    OutgoingMessageBuilder,
    ReplyMessageBuilder,
)
from pybotx.domain.models.message.reply import Reply
from pybotx.domain.models.message.reply_message import ReplyMessage
from pybotx.domain.widgets import MultiMessageWidget, SingleMessageWidget
from pybotx.application.widgets.session import (
    MultiWidgetState,
    SingleWidgetState,
    WidgetSession,
    WidgetState,
)
from pybotx.application.widgets.factory import WidgetFactory
from pybotx.presentation.contracts.method_callbacks import (
    BotAPIMethodFailedCallback,
    BotAPIMethodSuccessfulCallback,
    BotXMethodCallback,
)
from pybotx.domain.models.smartapps import SmartApp
from pybotx.domain.models.status import BotMenu, StatusRecipient
from pybotx.domain.models.stickers import Sticker, StickerPack, StickerPackFromList
from pybotx.presentation.contracts.sync_smartapp_event import (
    BotAPISyncSmartAppEventErrorResponse,
    BotAPISyncSmartAppEventResponse,
    BotAPISyncSmartAppEventResultResponse,
)
from pybotx.domain.models.sync_smartapp_event import (
    SyncSmartAppEventError,
    SyncSmartAppEventResponse,
    SyncSmartAppEventResult,
)
from pybotx.domain.models.system_events.added_to_chat import AddedToChatEvent
from pybotx.domain.models.system_events.chat_created import ChatCreatedEvent, ChatCreatedMember
from pybotx.domain.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent
from pybotx.domain.models.system_events.conference_changed import ConferenceChangedEvent
from pybotx.domain.models.system_events.conference_created import ConferenceCreatedEvent
from pybotx.domain.models.system_events.conference_deleted import ConferenceDeletedEvent
from pybotx.domain.models.system_events.cts_login import CTSLoginEvent
from pybotx.domain.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.domain.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.domain.models.system_events.event_delete import EventDeleted
from pybotx.domain.models.system_events.event_edit import EventEdit
from pybotx.domain.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.domain.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent
from pybotx.domain.models.users import UserFromCSV, UserFromSearch

__all__ = (
    "AddedToChatEvent",
    "AnswerDestinationLookupError",
    "AttachmentDocument",
    "AttachmentImage",
    "AttachmentTypes",
    "AttachmentVideo",
    "AttachmentVoice",
    "AttachmentFactoryPort",
    "WidgetStateStorePort",
    "AioHttpClientAdapter",
    "AiohttpAdapter",
    "AttachmentFactory",
    "InMemoryWidgetStateStore",
    "JsonWidgetStateSerializer",
    "PickleWidgetStateSerializer",
    "RedisWidgetStateStore",
    "WidgetStateSerializer",
    "DjangoNinjaAdapter",
    "Bot",
    "BotAPIBotDisabledErrorData",
    "BotAPIBotDisabledResponse",
    "BotAPIMethodFailedCallback",
    "BotAPIMethodSuccessfulCallback",
    "BotAPISyncSmartAppEventErrorResponse",
    "BotAPISyncSmartAppEventResponse",
    "BotAPISyncSmartAppEventResultResponse",
    "SyncSmartAppEventError",
    "SyncSmartAppEventResponse",
    "SyncSmartAppEventResult",
    "BotAPIUnverifiedRequestErrorData",
    "BotAPIUnverifiedRequestResponse",
    "BotAccount",
    "BotAccountWithSecret",
    "BotXAuthVersion",
    "BotCommandValidationError",
    "BotXContainer",
    "BotIsNotChatMemberError",
    "BotMenu",
    "BotSender",
    "BotShuttingDownError",
    "BotXValidationError",
    "BotXMethodCallbackNotFoundError",
    "BotXMethodFailedCallbackReceivedError",
    "BotXMethodCallback",
    "BotsListItem",
    "BubbleMarkup",
    "Button",
    "ButtonRow",
    "ButtonTextAlign",
    "BulkEditItemResult",
    "BulkEditResult",
    "BulkReplyItemResult",
    "BulkReplyResult",
    "BulkSendItemResult",
    "BulkSendResult",
    "CTSLoginEvent",
    "CTSLogoutEvent",
    "CallbackNotReceivedError",
    "CallbackRepoProto",
    "CantUpdatePersonalChatError",
    "Chat",
    "ChatCreatedEvent",
    "ChatCreatedMember",
    "ChatCreationError",
    "ChatCreationProhibitedError",
    "ChatDeletedByUserEvent",
    "ChatInfo",
    "ChatInfoMember",
    "ChatLink",
    "ChatLinkCreationError",
    "ChatLinkCreationProhibitedError",
    "ChatListItem",
    "ChatNotFoundError",
    "ChatLinkTypes",
    "ChatTypes",
    "ClientPlatforms",
    "CommandDescriptionRequiredError",
    "ConferenceChangedEvent",
    "ConferenceCreatedEvent",
    "ConferenceDeletedEvent",
    "ConferenceLinkTypes",
    "DeletedFromChatEvent",
    "Document",
    "EditMessage",
    "EventDeleted",
    "EventEdit",
    "EventNotFoundError",
    "File",
    "FileDeletedError",
    "FileMetadataNotFound",
    "FastAPIAdapter",
    "FinalRecipientsListEmptyError",
    "Forward",
    "HandlerCollector",
    "HandlerAlreadyRegisteredError",
    "Image",
    "IncomingMessage",
    "IncomingMessageHandlerFunc",
    "InternalBotNotificationEvent",
    "InvalidAvatarDataError",
    "InvalidBotAccountError",
    "TransportError",
    "InvalidBotXResponsePayloadError",
    "InvalidBotXStatusCodeError",
    "InvalidBotCommandLinkError",
    "InvalidCommandNameError",
    "InvalidCtsUrlError",
    "InvalidEmojiError",
    "InvalidImageError",
    "InvalidMarkupError",
    "InvalidWidgetPayloadError",
    "InvalidStickerImageError",
    "InvalidUsersListError",
    "InvalidWebhookPayloadError",
    "JwtEncodingError",
    "KeyboardMarkup",
    "LeftFromChatEvent",
    "LoggerPort",
    "Mention",
    "MentionAll",
    "MentionBuilder",
    "MentionChannel",
    "MentionChat",
    "MentionContact",
    "MentionList",
    "MentionTypes",
    "MentionUser",
    "MentionComposer",
    "TextBuilder",
    "MessageNotFoundError",
    "MessageStatus",
    "MessageOptions",
    "NotificationOptions",
    "Middleware",
    "MultiWidgetState",
    "MultiWidgetSendResult",
    "NotificationBodyTooLongError",
    "OutgoingAttachment",
    "OutgoingMessage",
    "OutgoingMessageBuilder",
    "ReplyMessageBuilder",
    "EditMessageBuilder",
    "PermissionDeniedError",
    "RateLimitReachedError",
    "Reply",
    "ReplyMessage",
    "SingleMessageWidget",
    "SingleWidgetState",
    "WidgetFactory",
    "WidgetSession",
    "WidgetState",
    "MultiMessageWidget",
    "RequestHeadersNotProvidedError",
    "SmartApp",
    "SmartAppEvent",
    "SmartappManifest",
    "SmartappManifestAndroidParams",
    "SmartappManifestAuroraParams",
    "SmartappManifestIosParams",
    "SmartappManifestUnreadCounterParams",
    "SmartappManifestWebLayoutChoices",
    "SmartappManifestWebParams",
    "StatusRequestValidationError",
    "StatusRecipient",
    "StealthModeDisabledError",
    "StickerImageTooLargeError",
    "Sticker",
    "StickerPack",
    "StickerPackFromList",
    "StickerPackOrStickerNotFoundError",
    "SyncSmartAppEventValidationError",
    "SyncSmartAppEventHandlerFunc",
    "SyncSmartAppEventHandlerNotFoundError",
    "SyncSourceTypes",
    "TestkitConfigurationError",
    "ThreadAlreadyExistsError",
    "ThreadCreationError",
    "ThreadCreationProhibitedError",
    "UnknownBotAccountError",
    "UnknownSystemEventError",
    "UnsupportedBotAPIVersionError",
    "UnverifiedRequestError",
    "UserDevice",
    "UserFromCSV",
    "UserFromSearch",
    "UserKinds",
    "UserNotFoundError",
    "UserSender",
    "Video",
    "Voice",
    "build_bot_disabled_response",
    "build_bot_command_link",
    "build_bot",
    "build_command_accepted_response",
    "build_default_config",
    "build_aiohttp_app",
    "wrap_asgi_app",
    "build_django_ninja_router",
    "build_fastapi_router",
    "build_unverified_request_response",
    "lifespan_wrapper",
)

def __getattr__(name: str):  # type: ignore[override]
    if name in {"AiohttpAdapter", "build_aiohttp_app"}:
        try:
            from pybotx.presentation.aiohttp import AiohttpAdapter, build_aiohttp_app
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "aiohttp integration requires optional dependency `aiohttp`."
            ) from exc

        return {
            "AiohttpAdapter": AiohttpAdapter,
            "build_aiohttp_app": build_aiohttp_app,
        }[name]
    if name in {"DjangoNinjaAdapter", "build_django_ninja_router"}:
        try:
            from pybotx.presentation.django_ninja import (
                DjangoNinjaAdapter,
                build_django_ninja_router,
            )
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "Django Ninja integration requires optional dependencies "
                "`django` and `django-ninja`."
            ) from exc

        return {
            "DjangoNinjaAdapter": DjangoNinjaAdapter,
            "build_django_ninja_router": build_django_ninja_router,
        }[name]
    if name == "wrap_asgi_app":
        from pybotx.presentation.asgi_lifespan import wrap_asgi_app

        return wrap_asgi_app
    if name in {"FastAPIAdapter", "build_fastapi_router"}:
        try:
            from pybotx.presentation.fastapi import FastAPIAdapter, build_fastapi_router
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "FastAPI integration requires optional dependency `fastapi`."
            ) from exc

        return {
            "FastAPIAdapter": FastAPIAdapter,
            "build_fastapi_router": build_fastapi_router,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

logger.disable("pybotx")
