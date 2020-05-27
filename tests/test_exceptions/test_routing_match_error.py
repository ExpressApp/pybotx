import pytest

from botx.exceptions import NoMatchFound

pytestmark = pytest.mark.asyncio


async def test_search_param_in_matching_error(bot, message, client):
    with pytest.raises(NoMatchFound) as err_info:
        await bot.collector.handle_message(message)

    error = err_info.value
    assert error.search_param == message.command.body
