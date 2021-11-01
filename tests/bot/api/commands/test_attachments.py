from typing import Any, Callable, Dict, Optional

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

API_AND_DOMAIN_NON_FILE_ATTACHMENTS = (
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
    "api_attachment,domain_attachment,attr_name",
    API_AND_DOMAIN_NON_FILE_ATTACHMENTS,
)
async def test__async_execute_raw_bot_command__non_file_attachments_types(
    api_attachment: Dict[str, Any],
    domain_attachment: IncomingAttachment,
    attr_name: str,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    payload = incoming_message_payload_factory(attachment=api_attachment)

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
    assert getattr(incoming_message, attr_name) == domain_attachment


API_AND_DOMAIN_FILE_ATTACHMENTS = (
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
    "api_attachment,domain_attachment",
    API_AND_DOMAIN_FILE_ATTACHMENTS,
)
async def test__async_execute_raw_bot_command__file_attachments_types(
    api_attachment: Dict[str, Any],
    domain_attachment: IncomingAttachment,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    payload = incoming_message_payload_factory(attachment=api_attachment)

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
    assert incoming_message.file == domain_attachment  # type: ignore [union-attr]
