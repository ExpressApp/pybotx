import asyncio
from typing import Optional
from uuid import UUID

import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, IncomingMessage, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
async def test__attachment__open(
    chat_id: UUID,
    host: str,
    file_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": bot_id,
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
        "async_files": [],
        "attachments": [
            {
                "data": {
                    "content": "data:image/jpg;base64,SGVsbG8sIHdvcmxkIQo=",
                    "file_name": "test_file.jpg",
                },
                "type": "image",
            },
        ],
        "source_sync_id": "bc3d06ed-7b2e-41ad-99f9-ca28adc2c88d",
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": "domain",
            "ad_login": "login",
            "app_version": "1.21.9",
            "chat_type": "chat",
            "device": "Firefox 91.0",
            "device_meta": {
                "permissions": {
                    "microphone": True,
                    "notifications": False,
                },
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": "Linux",
            "group_chat_id": chat_id,
            "host": host,
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": "Mozilla",
            "platform": "web",
            "platform_package_id": "ru.unlimitedtech.express",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": "Ivanov Ivan Ivanovich",
        },
        "proto_version": 4,
    }

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
