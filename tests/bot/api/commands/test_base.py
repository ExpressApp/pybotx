import pytest

from botx import Bot, HandlerCollector, UnsupportedBotAPIVersionError, lifespan_wrapper


@pytest.mark.asyncio
async def test_handle_decoding_error() -> None:
    # - Arrange -
    payload = "{invalid: json"
    built_bot = Bot(collectors=[HandlerCollector()])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "decoding JSON" in str(exc)


@pytest.mark.asyncio
async def test_handle_validation_error() -> None:
    # - Arrange -
    payload = '{"invalid": "command"}'
    built_bot = Bot(collectors=[HandlerCollector()])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "validation" in str(exc)


@pytest.mark.asyncio
async def test_handle_invalid_bot_api_version() -> None:
    # - Arrange -
    payload = '{"proto_version": "3"}'
    built_bot = Bot(collectors=[HandlerCollector()])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnsupportedBotAPIVersionError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "Unsupported" in str(exc)
    assert "expected `4`" in str(exc)
