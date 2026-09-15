from pybotx import (
    AnyOfBotXRetryRequestPolicy,
    BotXOperation,
    BotXRequestMetadata,
    BotXRetryPolicy,
    KnownSafeBotXRetryRequestPolicy,
    OperationNameAllowlistBotXRetryRequestPolicy,
    PathAllowlistBotXRetryRequestPolicy,
    RetryAllBotXRequestsPolicy,
    SafeBotXRetryRequestPolicy,
)
import pytest
from pybotx.client.http_config import iter_retry_request_policy_warnings
from typing import Any


def test__botx_operation__has_str_enum_semantics() -> None:
    assert str(BotXOperation.CHAT_INFO) == "ChatInfoMethod"


def test__safe_botx_retry_request_policy__retries_get_requests() -> None:
    policy = SafeBotXRetryRequestPolicy()

    assert policy.should_retry(
        BotXRequestMetadata(method="GET", url="https://cts.example.com/api/v3/botx/chats/list"),
    )


def test__safe_botx_retry_request_policy__retries_allowlisted_post_requests() -> None:
    policy = SafeBotXRetryRequestPolicy()

    assert policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v3/botx/users/by_email",
        ),
    )


def test__safe_botx_retry_request_policy__does_not_retry_unsafe_post_requests() -> None:
    policy = SafeBotXRetryRequestPolicy()

    assert not policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
        ),
    )


def test__path_allowlist_botx_retry_request_policy__normalizes_uuid_path_segments() -> None:
    policy = PathAllowlistBotXRetryRequestPolicy(
        allowed_requests={("GET", "/api/v3/botx/events/{uuid}/status")},
    )

    assert policy.should_retry(
        BotXRequestMetadata(
            method="GET",
            url=(
                "https://cts.example.com/api/v3/botx/events/"
                "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3/status"
            ),
        ),
    )


def test__retry_all_botx_requests_policy__retries_everything() -> None:
    policy = RetryAllBotXRequestsPolicy()

    assert policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
        ),
    )


def test__operation_name_allowlist_botx_retry_request_policy__matches_operation_name() -> None:
    policy = OperationNameAllowlistBotXRetryRequestPolicy(
        operation_names={BotXOperation.CHAT_INFO, BotXOperation.MESSAGE_STATUS},
    )

    assert policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
            operation_name="MessageStatusMethod",
        ),
    )
    assert not policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
            operation_name="DirectNotificationMethod",
        ),
    )


def test__known_safe_botx_retry_request_policy__retries_known_safe_operation() -> None:
    policy = KnownSafeBotXRetryRequestPolicy()

    assert policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v3/botx/users/by_email",
            operation_name=BotXOperation.SEARCH_USER_BY_EMAIL_POST,
        ),
    )
    assert not policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
            operation_name=BotXOperation.DIRECT_NOTIFICATION,
        ),
    )


def test__any_of_botx_retry_request_policy__retries_when_any_nested_policy_matches() -> None:
    policy = AnyOfBotXRetryRequestPolicy(
        policies=(
            SafeBotXRetryRequestPolicy(),
            OperationNameAllowlistBotXRetryRequestPolicy(
                operation_names={BotXOperation.DIRECT_NOTIFICATION},
            ),
        ),
    )

    assert policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
            operation_name=BotXOperation.DIRECT_NOTIFICATION,
        ),
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"initial_delay_seconds": -1},
        {"max_delay_seconds": -1},
        {"initial_delay_seconds": 2, "max_delay_seconds": 1},
        {"jitter_seconds": -1},
    ],
)
def test__botx_retry_policy__rejects_invalid_values(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        BotXRetryPolicy(**kwargs)


def test__retry_policies__cover_optional_configuration_and_warning_paths() -> None:
    metadata_without_operation = BotXRequestMetadata(method="POST", url="https://cts.test")
    operation_policy = OperationNameAllowlistBotXRetryRequestPolicy(operation_names=set())
    assert operation_policy.should_retry(metadata_without_operation) is False

    known_safe = KnownSafeBotXRetryRequestPolicy(extra_operations={"CustomWrite"})
    assert "CustomWrite" in known_safe.get_operation_names()
    assert iter_retry_request_policy_warnings(known_safe)
    assert iter_retry_request_policy_warnings(
        OperationNameAllowlistBotXRetryRequestPolicy(operation_names={"CustomWrite"}),
    )
    assert iter_retry_request_policy_warnings(
        OperationNameAllowlistBotXRetryRequestPolicy(
            operation_names={BotXOperation.CHAT_INFO},
        ),
    ) == ()

    path_policy = PathAllowlistBotXRetryRequestPolicy(
        allowed_requests={("post", "/write")},
        path_normalizer=lambda _url: "/write",
    )
    assert path_policy.get_allowed_requests() == frozenset({("POST", "/write")})
    assert iter_retry_request_policy_warnings(path_policy)

    safe = SafeBotXRetryRequestPolicy(
        safe_methods={"TRACE"},
        extra_safe_requests={("post", "/write")},
        extra_safe_operation_names={"CustomWrite"},
        path_normalizer=lambda _url: "/write",
    )
    assert safe.should_retry(metadata_without_operation)
    assert iter_retry_request_policy_warnings(safe)
    assert iter_retry_request_policy_warnings(
        AnyOfBotXRetryRequestPolicy(policies=(RetryAllBotXRequestsPolicy(),)),
    )
