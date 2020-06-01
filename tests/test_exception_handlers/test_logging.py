import pytest

pytestmark = pytest.mark.asyncio


async def test_logging_that_handler_was_not_found(
    bot, client, incoming_message, loguru_caplog,
) -> None:
    await client.send_command(incoming_message)

    error_message = "handler for {0} was not found".format(
        incoming_message.command.body,
    )

    assert error_message in loguru_caplog.text
