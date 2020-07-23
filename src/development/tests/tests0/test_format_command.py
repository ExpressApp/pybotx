import pytest

from botx import Bot, MessageBuilder, TestClient


@pytest.mark.asyncio
async def test_hello_format(
    bot: Bot, builder: MessageBuilder, client: TestClient
) -> None:
    builder.body = "/hello"

    await client.send_command(builder.message)

    command_result = client.command_results[0]
    assert command_result.result.body == f"Hello, {builder.user.username}"
