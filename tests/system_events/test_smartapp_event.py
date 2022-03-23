from typing import Optional
from uuid import UUID

import pytest

from pybotx import (
    AttachmentTypes,
    Bot,
    BotAccount,
    BotAccountWithSecret,
    HandlerCollector,
    Image,
    SmartAppEvent,
    lifespan_wrapper,
)
from pybotx.models.chats import Chat
from pybotx.models.enums import ChatTypes
from pybotx.models.message.incoming_message import UserDevice, UserSender

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__smartapp__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:smartapp_event",
            "data": {
                "ref": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "smartapp_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "data": {
                    "type": "smartapp_rpc",
                    "method": "folders.get",
                    "params": {
                        "q": 1,
                    },
                },
                "opts": {"option": "test_option"},
                "smartapp_api_version": 1,
            },
            "command_type": "system",
            "metadata": {},
        },
        "async_files": [
            {
                "type": "image",
                "file": "https://link.to/file",
                "file_mime_type": "image/png",
                "file_name": "pass.png",
                "file_preview": "https://link.to/preview",
                "file_preview_height": 300,
                "file_preview_width": 300,
                "file_size": 1502345,
                "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                "file_encryption_algo": "stream",
                "chunk_size": 2097152,
                "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
            },
        ],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": "b9197d3a-d855-5d34-ba8a-eff3a975ab20",
            "group_chat_id": "dea55ee4-7a9f-5da0-8c73-079f400ee517",
            "host": "cts.example.com",
            "ad_login": None,
            "ad_domain": None,
            "username": None,
            "chat_type": "group_chat",
            "manufacturer": None,
            "device": None,
            "device_software": None,
            "device_meta": {},
            "platform": None,
            "platform_package_id": None,
            "is_admin": False,
            "is_creator": False,
            "app_version": None,
            "locale": "en",
        },
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    smartapp: Optional[SmartAppEvent] = None

    @collector.smartapp_event
    async def smartapp_handler(event: SmartAppEvent, bot: Bot) -> None:
        nonlocal smartapp
        smartapp = event
        # Drop `raw_command` from asserting
        smartapp.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert smartapp == SmartAppEvent(
        ref=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        smartapp_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        data={
            "type": "smartapp_rpc",
            "method": "folders.get",
            "params": {
                "q": 1,
            },
        },
        opts={"option": "test_option"},
        smartapp_api_version=1,
        files=[
            Image(
                type=AttachmentTypes.IMAGE,
                filename="pass.png",
                size=1502345,
                is_async_file=True,
                _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
                _file_url="https://link.to/file",
                _file_mimetype="image/png",
                _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
            ),
        ],
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        sender=UserSender(
            huid=UUID("b9197d3a-d855-5d34-ba8a-eff3a975ab20"),
            ad_login=None,
            ad_domain=None,
            username=None,
            is_chat_admin=False,
            is_chat_creator=False,
            device=UserDevice(
                manufacturer=None,
                device_name=None,
                os=None,
                pushes=None,
                timezone=None,
                permissions=None,
                platform=None,
                platform_package_id=None,
                app_version=None,
                locale="en",
            ),
        ),
        raw_command=None,
    )
