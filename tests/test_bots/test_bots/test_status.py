import pytest

pytestmark = pytest.mark.asyncio


async def test_returning_bot_commands_status(bot, collector_with_handlers):
    bot.include_collector(collector_with_handlers)
    status = await bot.status()
    commands = [command.body for command in status.result.commands]
    assert commands == [
        "/regular-handler",
        "/handler-command",
        "/handler-command1",
        "/handler-command2",
        "/handler-command3",
        "/handler-command4",
        "/handler-command5",
        "/regular-handler-with-name",
        "/regular-handler-with-background-dependencies",
        "/regular-handler-that-included-in-status-by-callable-function",
    ]
