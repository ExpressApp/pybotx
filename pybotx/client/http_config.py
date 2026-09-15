from dataclasses import dataclass, field
from enum import StrEnum
import re
from typing import Protocol
from collections.abc import Callable, Collection
from urllib.parse import urlsplit

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from pybotx.client.observability import BotXRequestMetadata
from pybotx.constants import (
    BOTX_HTTP_CONNECT_TIMEOUT_SECONDS,
    BOTX_HTTP_KEEPALIVE_EXPIRY_SECONDS,
    BOTX_HTTP_MAX_CONNECTIONS,
    BOTX_HTTP_MAX_KEEPALIVE_CONNECTIONS,
    BOTX_HTTP_POOL_TIMEOUT_SECONDS,
    BOTX_HTTP_READ_TIMEOUT_SECONDS,
    BOTX_HTTP_RETRY_ATTEMPTS,
    BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS,
    BOTX_HTTP_RETRY_JITTER_SECONDS,
    BOTX_HTTP_RETRY_MAX_DELAY_SECONDS,
    BOTX_HTTP_WRITE_TIMEOUT_SECONDS,
)

DEFAULT_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
RetryExceptionTypes = tuple[type[BaseException], ...]
BeforeSleepHandler = Callable[[RetryCallState], None]
AllowedRequestPattern = tuple[str, str]
PathNormalizer = Callable[[str], str]

_UUID_PATH_SEGMENT_RE = re.compile(
    r"/[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}(?=/|$)",
)


class BotXOperation(StrEnum):
    ADD_ADMIN = "AddAdminMethod"
    ADD_STICKER = "AddStickerMethod"
    ADD_USER = "AddUserMethod"
    BOTS_LIST = "BotsListMethod"
    CHAT_INFO = "ChatInfoMethod"
    COLLECT_BOT_FUNCTION = "CollectBotFunctionMethod"
    CREATE_CHAT = "CreateChatMethod"
    CREATE_CHAT_LINK = "CreateChatLinkMethod"
    CREATE_STICKER_PACK = "CreateStickerPackMethod"
    CREATE_THREAD = "CreateThreadMethod"
    DELETE_EVENT = "DeleteEventMethod"
    DELETE_STICKER = "DeleteStickerMethod"
    DELETE_STICKER_PACK = "DeleteStickerPackMethod"
    DIRECT_NOTIFICATION = "DirectNotificationMethod"
    DIRECT_NOTIFICATION_SYNC = "DirectNotificationSyncMethod"
    DISABLE_STEALTH = "DisableStealthMethod"
    DOWNLOAD_FILE = "DownloadFileMethod"
    EDIT_EVENT = "EditEventMethod"
    EDIT_STICKER_PACK = "EditStickerPackMethod"
    FILES_UPLOAD_FILE = "FilesUploadFileMethod"
    GET_STICKER = "GetStickerMethod"
    GET_STICKER_PACK = "GetStickerPackMethod"
    GET_STICKER_PACKS = "GetStickerPacksMethod"
    GET_TOKEN = "GetTokenMethod"
    INTERNAL_BOT_NOTIFICATION = "InternalBotNotificationMethod"
    LIST_CHATS = "ListChatsMethod"
    MESSAGE_STATUS = "MessageStatusMethod"
    PERSONAL_CHAT = "PersonalChatMethod"
    PIN_MESSAGE = "PinMessageMethod"
    REFRESH_ACCESS_TOKEN = "RefreshAccessTokenMethod"
    REMOVE_USER = "RemoveUserMethod"
    REPLY_EVENT = "ReplyEventMethod"
    SEARCH_USER_BY_EMAIL_GET = "SearchUserByEmailMethod"
    SEARCH_USER_BY_EMAIL_POST = "SearchUserByEmailPostMethod"
    SEARCH_USER_BY_EMAILS = "SearchUserByEmailsMethod"
    SEARCH_USER_BY_HUID = "SearchUserByHUIDMethod"
    SEARCH_USER_BY_LOGIN = "SearchUserByLoginMethod"
    SEARCH_USER_BY_OTHER_ID = "SearchUserByOtherIdMethod"
    SET_STEALTH = "SetStealthMethod"
    SMARTAPP_CUSTOM_NOTIFICATION = "SmartAppCustomNotificationMethod"
    SMARTAPP_EVENT = "SmartAppEventMethod"
    SMARTAPP_MANIFEST = "SmartAppManifestMethod"
    SMARTAPP_NOTIFICATION = "SmartAppNotificationMethod"
    SMARTAPP_UNREAD_COUNTER = "SmartAppUnreadCounterMethod"
    SMARTAPPS_LIST = "SmartAppsListMethod"
    SMARTAPPS_UPLOAD_FILE = "SmartAppsUploadFileMethod"
    STOP_TYPING_EVENT = "StopTypingEventMethod"
    TYPING_EVENT = "TypingEventMethod"
    UNPIN_MESSAGE = "UnpinMessageMethod"
    UPDATE_USERS_PROFILE = "UpdateUsersProfileMethod"
    USERS_AS_CSV = "UsersAsCSVMethod"


OperationName = str | BotXOperation


KNOWN_SAFE_BOTX_OPERATIONS = frozenset(
    {
        BotXOperation.BOTS_LIST,
        BotXOperation.CHAT_INFO,
        BotXOperation.DOWNLOAD_FILE,
        BotXOperation.GET_STICKER,
        BotXOperation.GET_STICKER_PACK,
        BotXOperation.GET_STICKER_PACKS,
        BotXOperation.LIST_CHATS,
        BotXOperation.MESSAGE_STATUS,
        BotXOperation.PERSONAL_CHAT,
        BotXOperation.SEARCH_USER_BY_EMAIL_GET,
        BotXOperation.SEARCH_USER_BY_EMAIL_POST,
        BotXOperation.SEARCH_USER_BY_EMAILS,
        BotXOperation.SEARCH_USER_BY_HUID,
        BotXOperation.SEARCH_USER_BY_LOGIN,
        BotXOperation.SEARCH_USER_BY_OTHER_ID,
        BotXOperation.SMARTAPPS_LIST,
        BotXOperation.USERS_AS_CSV,
    },
)
_KNOWN_SAFE_OPERATION_NAMES = frozenset(operation.value for operation in KNOWN_SAFE_BOTX_OPERATIONS)


def build_default_httpx_timeout() -> httpx.Timeout:
    return httpx.Timeout(
        connect=BOTX_HTTP_CONNECT_TIMEOUT_SECONDS,
        read=BOTX_HTTP_READ_TIMEOUT_SECONDS,
        write=BOTX_HTTP_WRITE_TIMEOUT_SECONDS,
        pool=BOTX_HTTP_POOL_TIMEOUT_SECONDS,
    )


def build_default_httpx_limits() -> httpx.Limits:
    return httpx.Limits(
        max_connections=BOTX_HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=BOTX_HTTP_MAX_KEEPALIVE_CONNECTIONS,
        keepalive_expiry=BOTX_HTTP_KEEPALIVE_EXPIRY_SECONDS,
    )


def _normalize_operation_name(operation_name: OperationName) -> str:
    if isinstance(operation_name, BotXOperation):
        return operation_name.value
    return operation_name


@dataclass(frozen=True, slots=True)
class BotXRetryPolicy:
    max_attempts: int = BOTX_HTTP_RETRY_ATTEMPTS
    initial_delay_seconds: float = BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS
    max_delay_seconds: float = BOTX_HTTP_RETRY_MAX_DELAY_SECONDS
    jitter_seconds: float = BOTX_HTTP_RETRY_JITTER_SECONDS
    retryable_status_codes: frozenset[int] = field(
        default_factory=lambda: DEFAULT_RETRYABLE_STATUS_CODES,
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("Retry max attempts should be greater than 0")
        if self.initial_delay_seconds < 0:
            raise ValueError("Retry initial delay should be greater or equal to 0")
        if self.max_delay_seconds < 0:
            raise ValueError("Retry max delay should be greater or equal to 0")
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError(
                "Retry max delay should be greater or equal to initial delay",
            )
        if self.jitter_seconds < 0:
            raise ValueError("Retry jitter should be greater or equal to 0")


class BotXRetryStrategy(Protocol):
    def build_retrying(  # pragma: no cover
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: RetryExceptionTypes,
        before_sleep: BeforeSleepHandler,
    ) -> AsyncRetrying: ...


class BotXRetryRequestPolicy(Protocol):
    """Decides whether a specific BotX request may be retried automatically."""

    def should_retry(  # pragma: no cover
        self,
        metadata: BotXRequestMetadata,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class RetryAllBotXRequestsPolicy(BotXRetryRequestPolicy):
    """Retries every request matched by retry_policy."""

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        return True


class OperationNameAllowlistBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    """Retries only requests whose operation_name matches the allowlist."""

    def __init__(self, *, operation_names: Collection[OperationName]) -> None:
        self._operation_names = frozenset(
            _normalize_operation_name(operation_name)
            for operation_name in operation_names
        )

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        operation_name = metadata.operation_name
        if operation_name is None:
            return False
        return operation_name in self._operation_names

    def get_operation_names(self) -> frozenset[str]:
        return self._operation_names


class KnownSafeBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    """Retries only built-in pybotx operations from the known-safe catalog."""

    def __init__(
        self,
        *,
        extra_operations: Collection[OperationName] | None = None,
    ) -> None:
        operation_names = set(_KNOWN_SAFE_OPERATION_NAMES)
        if extra_operations is not None:
            operation_names.update(
                _normalize_operation_name(operation_name)
                for operation_name in extra_operations
            )
        self._operation_policy = OperationNameAllowlistBotXRetryRequestPolicy(
            operation_names=operation_names,
        )

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        return self._operation_policy.should_retry(metadata)

    def get_operation_names(self) -> frozenset[str]:
        return self._operation_policy.get_operation_names()


class PathAllowlistBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    """Retries only requests that match the configured method/path allowlist."""

    def __init__(
        self,
        *,
        allowed_requests: Collection[AllowedRequestPattern],
        path_normalizer: PathNormalizer | None = None,
    ) -> None:
        self._allowed_requests = frozenset(
            (method.upper(), path)
            for method, path in allowed_requests
        )
        self._path_normalizer = path_normalizer or self._default_path_normalizer

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        normalized_path = self._path_normalizer(metadata.url)
        return (metadata.method.upper(), normalized_path) in self._allowed_requests

    def get_allowed_requests(self) -> frozenset[AllowedRequestPattern]:
        return self._allowed_requests

    @staticmethod
    def _default_path_normalizer(url: str) -> str:
        parsed = urlsplit(url)
        path = parsed.path or "/"
        return _UUID_PATH_SEGMENT_RE.sub("/{uuid}", path)


class _MethodAllowlistBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    def __init__(self, *, methods: Collection[str]) -> None:
        self._methods = frozenset(method.upper() for method in methods)

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        return metadata.method.upper() in self._methods


class AnyOfBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    """Retries when any nested policy allows retry."""

    def __init__(self, *, policies: Collection[BotXRetryRequestPolicy]) -> None:
        self._policies = tuple(policies)

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        return any(policy.should_retry(metadata) for policy in self._policies)

    def get_policies(self) -> tuple[BotXRetryRequestPolicy, ...]:
        return self._policies


class SafeBotXRetryRequestPolicy(BotXRetryRequestPolicy):
    """Safe default for BotX: retry only read-only requests."""

    DEFAULT_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
    DEFAULT_SAFE_REQUESTS = frozenset(
        {
            ("POST", "/api/v3/botx/users/by_email"),
        },
    )

    def __init__(
        self,
        *,
        safe_methods: Collection[str] | None = None,
        extra_safe_requests: Collection[AllowedRequestPattern] | None = None,
        extra_safe_operation_names: Collection[str] | None = None,
        path_normalizer: PathNormalizer | None = None,
    ) -> None:
        methods = safe_methods or self.DEFAULT_SAFE_METHODS
        allowlist = set(self.DEFAULT_SAFE_REQUESTS)
        if extra_safe_requests is not None:
            allowlist.update(
                (method.upper(), path)
                for method, path in extra_safe_requests
            )
        policies: list[BotXRetryRequestPolicy] = [
            _MethodAllowlistBotXRetryRequestPolicy(methods=methods),
            PathAllowlistBotXRetryRequestPolicy(
                allowed_requests=allowlist,
                path_normalizer=path_normalizer,
            ),
        ]
        if extra_safe_operation_names is not None:
            policies.append(
                OperationNameAllowlistBotXRetryRequestPolicy(
                    operation_names=extra_safe_operation_names,
                ),
            )
        self._policy = AnyOfBotXRetryRequestPolicy(policies=policies)

    def should_retry(self, metadata: BotXRequestMetadata) -> bool:
        return self._policy.should_retry(metadata)


def iter_retry_request_policy_warnings(
    policy: BotXRetryRequestPolicy,
) -> tuple[str, ...]:
    warnings: list[str] = []
    _collect_retry_request_policy_warnings(policy, warnings)
    return tuple(dict.fromkeys(warnings))


def _collect_retry_request_policy_warnings(
    policy: BotXRetryRequestPolicy,
    warnings: list[str],
) -> None:
    if isinstance(policy, RetryAllBotXRequestsPolicy):
        warnings.append(
            "RetryAllBotXRequestsPolicy retries all BotX requests, including "
            "write operations. Verify idempotency or external deduplication.",
        )
        return

    if isinstance(policy, KnownSafeBotXRetryRequestPolicy):
        unsafe_operations = sorted(
            operation_name
            for operation_name in policy.get_operation_names()
            if operation_name not in _KNOWN_SAFE_OPERATION_NAMES
        )
        if unsafe_operations:
            warnings.append(
                "KnownSafeBotXRetryRequestPolicy has extra operations outside the "
                f"known-safe catalog: {', '.join(unsafe_operations)}. Verify "
                "idempotency manually.",
            )
        return

    if isinstance(policy, OperationNameAllowlistBotXRetryRequestPolicy):
        unsafe_operations = sorted(
            operation_name
            for operation_name in policy.get_operation_names()
            if operation_name not in _KNOWN_SAFE_OPERATION_NAMES
        )
        if unsafe_operations:
            warnings.append(
                "OperationNameAllowlistBotXRetryRequestPolicy allows operations "
                f"outside the known-safe catalog: {', '.join(unsafe_operations)}. "
                "Verify idempotency manually.",
            )
        return

    if isinstance(policy, PathAllowlistBotXRetryRequestPolicy):
        risky_requests = sorted(
            f"{method} {path}"
            for method, path in policy.get_allowed_requests()
            if method.upper() not in SafeBotXRetryRequestPolicy.DEFAULT_SAFE_METHODS
            and (method.upper(), path) not in SafeBotXRetryRequestPolicy.DEFAULT_SAFE_REQUESTS
        )
        if risky_requests:
            warnings.append(
                "PathAllowlistBotXRetryRequestPolicy allows requests outside the "
                f"known-safe set: {', '.join(risky_requests)}. Verify idempotency "
                "manually.",
            )
        return

    if isinstance(policy, SafeBotXRetryRequestPolicy):
        _collect_retry_request_policy_warnings(policy._policy, warnings)
        return

    if isinstance(policy, AnyOfBotXRetryRequestPolicy):
        for nested_policy in policy.get_policies():
            _collect_retry_request_policy_warnings(nested_policy, warnings)


@dataclass(frozen=True, slots=True)
class TenacityRetryStrategy(BotXRetryStrategy):
    def build_retrying(
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: RetryExceptionTypes,
        before_sleep: BeforeSleepHandler,
    ) -> AsyncRetrying:
        return AsyncRetrying(
            stop=stop_after_attempt(retry_policy.max_attempts),
            wait=wait_exponential_jitter(
                initial=retry_policy.initial_delay_seconds,
                max=retry_policy.max_delay_seconds,
                jitter=retry_policy.jitter_seconds,
            ),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep,
            reraise=True,
        )
