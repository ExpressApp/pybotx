from datetime import datetime
from typing import Any
from collections.abc import Callable
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import jwt
import pytest

from pybotx import (
    build_bot,
    Bot,
    BotAccountWithSecret,
    BotMenu,
    HandlerCollector,
    RequestHeadersNotProvidedError,
    UnverifiedRequestError,
    lifespan_wrapper,
)
from pybotx.domain.models.sync_smartapp_event import SyncSmartAppEventResult
from pybotx.presentation.raw_handlers import (
    async_execute_raw_bot_command,
    raw_get_status,
    set_raw_botx_method_result,
    sync_execute_raw_smartapp_event,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__verify_request__success_attempt(
    bot_account: BotAccountWithSecret,
    authorization_header: dict[str, str],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        bot._verify_request(authorization_header)


async def test__verify_request__no_authorization_header_provided(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({})

    # - Assert -
    assert "The authorization token was not provided." in str(exc.value)


async def test__verify_request__cannot_decode_token(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError):
            bot._verify_request({"authorization": "test"})


async def test__verify_request__aud_is_not_provided(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload.pop("aud")
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__aud_is_not_string(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["aud"] = 12345
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__aud_is_invalid_value(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["aud"] = "another.example.com"
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__v2_without_version_claim(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    del authorization_token_payload["version"]
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        bot._verify_request({"authorization": f"Bearer {token}"})


async def test__verify_request__unknown_issuer_value(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    random_bot_id = uuid4()
    authorization_token_payload["iss"] = str(random_bot_id)
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert f"No bot account with bot_id: `{random_bot_id!s}`" in str(exc.value)


async def test__verify_request__invalid_token_secret(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    token = jwt.encode(
        payload=authorization_token_payload,
        key=str(uuid4()),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Signature verification failed" in str(exc.value)


async def test__verify_request__expired_signature(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["exp"] = datetime(year=2000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Signature has expired" in str(exc.value)


async def test__verify_request__token_is_not_yet_valid_by_nbf(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["nbf"] = datetime(year=3000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "The token is not yet valid (nbf)" in str(exc.value)


async def test__verify_request__token_is_not_yet_valid_by_iat(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["iat"] = datetime(year=3000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "The token is not yet valid (iat)" in str(exc.value)


async def test__verify_request__invalid_issuer(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["iss"] = "another.example.com"
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid issuer" in str(exc.value)


async def test__verify_request__issuer_is_not_string(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    token_payload = dict(authorization_token_payload)
    token_payload["iss"] = 12345

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request_v2("token", token_payload, ["HS256"])

    # - Assert -
    assert "Invalid issuer" in str(exc.value)


async def test__verify_request__token_issuer_is_missed(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    del authorization_token_payload["iss"]
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot._verify_request(
                {"authorization": f"Bearer {token}"},
            )

    # - Assert -
    assert 'Token is missing the "iss" claim' in str(exc.value)


async def test__verify_request__compat_private_helpers(
    bot_account: BotAccountWithSecret,
) -> None:
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    async with lifespan_wrapper(built_bot) as bot:
        assert bot._is_v2_payload({"version": 2})
        with pytest.raises(UnverifiedRequestError):
            bot._verify_request_v1(
                "token",
                {"aud": "invalid"},
                ["HS256"],
                trusted_issuers=None,
            )


async def test__verify_request__without_headers__command(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError) as exc:
            async_execute_raw_bot_command(bot, payload, verify_request=True)

    assert "To verify the request you should provide headers." in str(exc.value)


async def test__verify_request__without_headers__smartapp(
    api_sync_smartapp_event_factory: Callable[..., dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
    bot_account: BotAccountWithSecret,
) -> None:
    built_bot = build_bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)

    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError) as exc:
            await sync_execute_raw_smartapp_event(bot, payload, verify_request=True)

    assert "To verify the request you should provide headers." in str(exc.value)


async def test__verify_request__without_headers__status(
    bot_account: BotAccountWithSecret,
) -> None:
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError) as exc:
            await raw_get_status(
                bot,
                {
                    "bot_id": str(bot_account.id),
                    "chat_type": "chat",
                    "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
                },
                verify_request=True,
            )

    assert "To verify the request you should provide headers." in str(exc.value)


async def test__verify_request__without_headers__callback(
    bot_account: BotAccountWithSecret,
) -> None:
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError) as exc:
            await set_raw_botx_method_result(
                bot,
                {
                    "status": "ok",
                    "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                    "result": {},
                },
                verify_request=True,
            )

    assert "To verify the request you should provide headers." in str(exc.value)


async def test__async_execute_raw_bot_command__verify_request__called(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        async_execute_raw_bot_command(bot, 
            payload,
            verify_request=True,
            request_headers={},
        )

    # - Assert -
    bot.verify_request.assert_called()


async def test__sync_execute_raw_smartapp_event__verify_request__called(
    api_sync_smartapp_event_factory: Callable[..., dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    built_bot = build_bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        await sync_execute_raw_smartapp_event(bot, 
            payload,
            verify_request=True,
            request_headers={},
        )

    # - Assert -
    bot.verify_request.assert_called()


async def test__raw_get_status__verify_request__called(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        await raw_get_status(bot, 
            {
                "bot_id": str(bot_account.id),
                "chat_type": "chat",
                "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            },
            verify_request=True,
            request_headers={},
        )

    # - Assert -
    bot.verify_request.assert_called()


async def test__set_raw_botx_method_result__verify_request__called(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.set_botx_method_result = AsyncMock()  # type: ignore
        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
            verify_request=True,
            request_headers={},
        )

    # - Assert -
    bot.verify_request.assert_called()


async def test__async_execute_raw_bot_command__verify_request__not_called(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.async_execute_bot_command = Mock()  # type: ignore
        async_execute_raw_bot_command(bot, payload, verify_request=False)

    # - Assert -
    bot.verify_request.assert_not_called()
    bot.async_execute_bot_command.assert_called()


async def test__sync_execute_raw_smartapp_event__verify_request__not_called(
    api_sync_smartapp_event_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_sync_smartapp_event_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.sync_execute_smartapp_event = AsyncMock(  # type: ignore
            return_value=SyncSmartAppEventResult(data={}),
        )
        await sync_execute_raw_smartapp_event(bot, payload, verify_request=False)

    # - Assert -
    bot.verify_request.assert_not_called()
    bot.sync_execute_smartapp_event.assert_awaited()


async def test__raw_get_status__verify_request__not_called(
    api_incoming_message_factory: Callable[..., dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.get_status = AsyncMock(return_value=BotMenu({}))  # type: ignore
        await raw_get_status(bot, 
            {
                "bot_id": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
                "chat_type": "chat",
                "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            },
            verify_request=False,
        )

    # - Assert -
    bot.verify_request.assert_not_called()
    bot.get_status.assert_awaited()


async def test__set_raw_botx_method_result__verify_request__not_called(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.set_botx_method_result = AsyncMock()  # type: ignore
        await set_raw_botx_method_result(bot, 
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    bot.verify_request.assert_not_called()
    bot.set_botx_method_result.assert_awaited()
