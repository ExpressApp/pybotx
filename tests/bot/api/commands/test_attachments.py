from typing import Any, Dict, Optional

import pytest

from botx import Bot, HandlerCollector, IncomingMessage, lifespan_wrapper
from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.domain.attachments import (
    AttachmentContact,
    AttachmentDocument,
    AttachmentImage,
    AttachmentLink,
    AttachmentLocation,
    AttachmentVideo,
    AttachmentVoice,
    IncomingAttachment,
)

API_AND_DOMAIN_ATTACHMENTS = (
    (
        {
            "type": "location",
            "data": {
                "location_name": "Центр вселенной",
                "location_address": "Россия, Тверская область",
                "location_lat": 58.04861,
                "location_lng": 34.28833,
            },
        },
        AttachmentLocation(
            type=AttachmentTypes.LOCATION,
            name="Центр вселенной",
            address="Россия, Тверская область",
            latitude="58.04861",
            longitude="34.28833",
        ),
        "location",
    ),
    (
        {
            "type": "contact",
            "data": {
                "file_name": "Контакт",
                "contact_name": "Иванов Иван",
                "content": "data:text/vcard;base64,eDnXAc1FEUB0VFEFctII3lRlRBcetROeFfduPmXxE/8=",
            },
        },
        AttachmentContact(
            type=AttachmentTypes.CONTACT,
            name="Иванов Иван",
        ),
        "contact",
    ),
    (
        {
            "type": "link",
            "data": {
                "url": "http://ya.ru/xxx",
                "url_title": "Header in link",
                "url_preview": "http://ya.ru/xxx.jpg",
                "url_text": "Some text in link",
            },
        },
        AttachmentLink(
            type=AttachmentTypes.LINK,
            url="http://ya.ru/xxx",
            title="Header in link",
            preview="http://ya.ru/xxx.jpg",
            text="Some text in link",
        ),
        "link",
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "attachment_json,attachment,attr_name",
    API_AND_DOMAIN_ATTACHMENTS,
)
async def test__async_execute_raw_bot_command__different_attachment_types(
    attachment_json: Dict[str, Any],
    attachment: IncomingAttachment,
    attr_name: str,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
        "attachments": [
            attachment_json,
        ],
        "async_files": [],
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
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
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

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert getattr(incoming_message, attr_name) == attachment


JSONS_WITH_DOMAINS_FILES = (
    (
        {
            "data": {
                "content": "data:image/jpg;base64,SGVsbG8sIHdvcmxkIQo=",
                "file_name": "test_file.jpg",
            },
            "type": "image",
        },
        AttachmentImage(
            type=AttachmentTypes.IMAGE,
            filename="test_file.jpg",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
        ),
    ),
    (
        {
            "data": {
                "content": "data:video/mp4;base64,SGVsbG8sIHdvcmxkIQo=",
                "file_name": "test_file.mp4",
                "duration": 10,
            },
            "type": "video",
        },
        AttachmentVideo(
            type=AttachmentTypes.VIDEO,
            filename="test_file.mp4",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
            duration=10,
        ),
    ),
    (
        {
            "data": {
                "content": "data:text/plain;base64,SGVsbG8sIHdvcmxkIQo=",
                "file_name": "test_file.txt",
            },
            "type": "document",
        },
        AttachmentDocument(
            type=AttachmentTypes.DOCUMENT,
            filename="test_file.txt",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
        ),
    ),
    (
        {
            "data": {
                "content": "data:audio/mpeg3;base64,SGVsbG8sIHdvcmxkIQo=",
                "duration": 10,
            },
            "type": "voice",
        },
        AttachmentVoice(
            type=AttachmentTypes.VOICE,
            filename="record.mp3",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
            duration=10,
        ),
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_json,file",
    JSONS_WITH_DOMAINS_FILES,
)
async def test__async_execute_raw_bot_command__different_file_types(
    file_json: Dict[str, Any],
    file: IncomingAttachment,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
        "attachments": [
            file_json,
        ],
        "async_files": [],
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
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
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

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert incoming_message.file == file  # type: ignore [union-attr]
