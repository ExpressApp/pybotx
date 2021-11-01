import asyncio
from typing import Any, Callable, Dict, Optional
from uuid import UUID

import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, IncomingMessage, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
async def test__attachment__open(
    chat_id: UUID,
    host: str,
    bot_account: BotAccount,
    bot_id: UUID,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
    mock_authorization: None,
) -> None:
    # - Arrange -
    payload = incoming_message_payload_factory(
        bot_id=bot_id,
        attachment={
            "data": {
                "content": "data:image/jpg;base64,SGVsbG8sIHdvcmxkIQo=",
                "file_name": "test_file.jpg",
            },
            "type": "image",
        },
        group_chat_id=chat_id,
        host=host,
    )
    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message

        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

        await asyncio.sleep(0)  # Return control to event loop
        async with incoming_message.file.open() as fo:  # type: ignore [union-attr]
            read_content = await fo.read()

    # - Assert -
    assert read_content == b"Hello, world!\n"
