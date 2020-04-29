import pytest
from _pytest.logging import LogCaptureFixture

from botx import Bot, IncomingMessage, TestClient


@pytest.mark.asyncio
async def test_logging_that_handler_was_not_found(
    bot: Bot,
    incoming_message: IncomingMessage,
    loguru_caplog: LogCaptureFixture,
    client: TestClient,
) -> None:
    bot.collector.default_message_handler = None

    await client.send_command(incoming_message)

    assert (
        f"handler for {incoming_message.command.body} was not found"
        in loguru_caplog.text
    )
