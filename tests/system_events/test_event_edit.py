from typing import Optional
from uuid import UUID

import pytest

from pybotx import (
    AttachmentTypes,
    Bot,
    BotAccount,
    BotAccountWithSecret,
    EventEdit,
    HandlerCollector,
    MentionContact,
    MentionTypes,
    lifespan_wrapper,
)
from pybotx.models.attachments import AttachmentImage

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__event_edit__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:event_edit",
            "data": {"body": "Edited"},
            "command_type": "system",
            "metadata": {},
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
        "entities": [
            {
                "type": "mention",
                "data": {
                    "mention_type": "contact",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {
                        "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
                        "name": "Вася Иванов",
                        "conn_type": "cts",
                    },
                },
            },
        ],
        "from": {
            "user_huid": None,
            "group_chat_id": None,
            "ad_login": None,
            "ad_domain": None,
            "username": None,
            "chat_type": None,
            "manufacturer": None,
            "device": None,
            "device_software": None,
            "device_meta": {},
            "platform": None,
            "platform_package_id": None,
            "is_admin": None,
            "is_creator": None,
            "app_version": None,
            "locale": "en",
            "host": "cts.example.com",
        },
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    event_edit: Optional[EventEdit] = None

    @collector.event_edit
    async def event_edit_handler(event: EventEdit, _: Bot) -> None:
        nonlocal event_edit
        event_edit = event
        # Drop `raw_command` from asserting
        event_edit.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert event_edit == EventEdit(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        raw_command=None,
        body="Edited",
        attachments=[
            AttachmentImage(
                type=AttachmentTypes.IMAGE,
                filename="test_file.jpg",
                size=14,
                is_async_file=False,
                content=b"Hello, world!\n",
            ),
        ],
        entities=[
            MentionContact(
                type=MentionTypes.CONTACT,
                entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
        ],
    )
