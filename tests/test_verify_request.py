from datetime import datetime
from typing import Any, Callable, Coroutine, Dict
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import jwt
import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotMenu,
    HandlerCollector,
    RequestHeadersNotProvidedError,
    UnverifiedRequestError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__verify_request__success_attempt(
    bot_account: BotAccountWithSecret,
    authorization_header: Dict[str, str],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request(authorization_header)


async def test__verify_request__no_authorization_header_provided(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({})

    # - Assert -
    assert "The authorization token was not provided." in str(exc.value)


async def test__verify_request__cannot_decode_token(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError):
            bot.verify_request({"authorization": "test"})


async def test__verify_request__aud_is_not_provided(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload.pop("aud")
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__aud_is_not_sequence(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["aud"] = 12345
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__too_many_aud_values(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["aud"] = [str(bot_account.id), str(uuid4())]
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid audience parameter was provided." in str(exc.value)


async def test__verify_request__unknown_aud_value(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    random_bot_id = uuid4()
    authorization_token_payload["aud"] = [str(random_bot_id)]
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert f"No bot account with bot_id: `{random_bot_id!s}`" in str(exc.value)


async def test__verify_request__invalid_token_secret(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    token = jwt.encode(
        payload=authorization_token_payload,
        key=str(uuid4()),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Signature verification failed" in str(exc.value)


async def test__verify_request__expired_signature(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["exp"] = datetime(year=2000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Signature has expired" in str(exc.value)


async def test__verify_request__token_is_not_yet_valid_by_nbf(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["nbf"] = datetime(year=3000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "The token is not yet valid (nbf)" in str(exc.value)


async def test__verify_request__token_is_not_yet_valid_by_iat(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["iat"] = datetime(year=3000, month=1, day=1).timestamp()
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "The token is not yet valid (iat)" in str(exc.value)


async def test__verify_request__invalid_issuer(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    authorization_token_payload["iss"] = "another.example.com"
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnverifiedRequestError) as exc:
            bot.verify_request({"authorization": f"Bearer {token}"})

    # - Assert -
    assert "Invalid issuer" in str(exc.value)


@pytest.mark.parametrize(
    "target_func_name",
    ("async_execute_raw_bot_command", "raw_get_status", "set_raw_botx_method_result"),
)
async def test__verify_request__without_headers(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
    target_func_name: str,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError) as exc:
            target_func = getattr(bot, target_func_name)
            result = target_func(payload, verify_request=True)
            if isinstance(result, Coroutine):
                await result

    # - Assert -
    assert "To verify the request you should provide headers." in str(exc.value)


async def test__async_execute_raw_bot_command__verify_request__called(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.async_execute_raw_bot_command(
            payload,
            verify_request=True,
            request_headers={},
        )

    # - Assert -
    bot.verify_request.assert_called()


async def test__raw_get_status__verify_request__called(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        await bot.raw_get_status(
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
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot._callbacks_manager.set_botx_method_callback_result = (  # type: ignore # noqa: WPS437
            AsyncMock()
        )
        await bot.set_raw_botx_method_result(
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
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])
    payload = api_incoming_message_factory()

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.async_execute_bot_command = Mock()  # type: ignore
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    bot.verify_request.assert_not_called()
    bot.async_execute_bot_command.assert_called()


async def test__raw_get_status__verify_request__not_called(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot.get_status = AsyncMock(return_value=BotMenu({}))  # type: ignore
        await bot.raw_get_status(
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
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.verify_request = Mock()  # type: ignore
        bot._callbacks_manager.set_botx_method_callback_result = (  # type: ignore # noqa: WPS437
            AsyncMock()
        )
        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    bot.verify_request.assert_not_called()
    bot._callbacks_manager.set_botx_method_callback_result.assert_awaited()  # noqa: WPS437
