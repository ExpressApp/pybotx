import pytest

from botx import Bot, HandlerCollector
from botx.testing import lifespan_wrapper


@pytest.mark.asyncio
async def test_handle_decoding_error() -> None:
    # - Arrange -
    payload = "{invalid: json"
    built_bot = Bot(collectors=[HandlerCollector()])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_botx_command(payload)

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
            bot.async_execute_raw_botx_command(payload)

    # - Assert -
    assert "validation" in str(exc)
