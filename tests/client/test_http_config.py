from pybotx import (
    AnyOfBotXRetryRequestPolicy,
    BotXOperation,
    BotXRequestMetadata,
    KnownSafeBotXRetryRequestPolicy,
    OperationNameAllowlistBotXRetryRequestPolicy,
    PathAllowlistBotXRetryRequestPolicy,
    RetryAllBotXRequestsPolicy,
    SafeBotXRetryRequestPolicy,
)


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
