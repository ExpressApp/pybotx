import pytest

from botx import Bot, HandlerCollector, UnsupportedBotAPIVersionError, lifespan_wrapper

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_execute_raw_bot_command__invalid_payload_value_error_raised() -> None:
    # - Arrange -
    payload = {"invalid": "command"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "validation" in str(exc.value)


async def test__async_execute_raw_bot_command__unsupported_bot_api_version_error_raised() -> None:
    # - Arrange -
    payload = {"proto_version": "3"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnsupportedBotAPIVersionError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "Unsupported" in str(exc.value)
    assert "expected `4`" in str(exc.value)
