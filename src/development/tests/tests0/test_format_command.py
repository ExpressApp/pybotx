import pytest
from botx import Bot, testing


@pytest.mark.asyncio
async def test_hello_format(bot: Bot, builder: testing.MessageBuilder) -> None:
    builder.body = "/hello"

    with testing.TestClient(bot) as client:
        await client.send_command(builder.message)

        command_result = client.command_results[0]
        assert command_result.result.body == f"Hello, {builder.user.username}"
