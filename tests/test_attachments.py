import asyncio
from typing import Any, Callable, Dict, Optional
from uuid import UUID

import pytest

from pybotx import (
    AttachmentTypes,
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    Sticker,
    lifespan_wrapper,
)
from pybotx.models.attachments import (
    AttachmentDocument,
    AttachmentImage,
    AttachmentVideo,
    AttachmentVoice,
    Contact,
    IncomingAttachment,
    Link,
    Location,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__attachment__open(
    host: str,
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(
        bot_id=bot_id,
        attachment={
            "data": {
                "content": "data:image/jpg;base64,SGVsbG8sIHdvcmxkIQo=",
                "file_name": "test_file.jpg",
            },
            "type": "image",
        },
        group_chat_id="054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

        await asyncio.sleep(0)  # Return control to event loop

        assert incoming_message and incoming_message.file
        async with incoming_message.file.open() as fo:
            read_content = await fo.read()

    # - Assert -
    assert read_content == b"Hello, world!\n"


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
        Location(
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
        Contact(
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
        Link(
            url="http://ya.ru/xxx",
            title="Header in link",
            preview="http://ya.ru/xxx.jpg",
            text="Some text in link",
        ),
        "link",
    ),
    (
        {
            "type": "sticker",
            "data": {
                "id": "0dfd7318-2ccc-5384-b0e4-6fa5478606a5",
                "link": "/uploads/sticker_pack/c81e87be5c7949b3b4196769e1032d5f.png",
                "pack": "4e4cfd0b-b981-54e9-84f4-3ddc12600334",
            },
        },
        Sticker(
            id=UUID("0dfd7318-2ccc-5384-b0e4-6fa5478606a5"),
            image_link="/uploads/sticker_pack/c81e87be5c7949b3b4196769e1032d5f.png",
            pack_id=UUID("4e4cfd0b-b981-54e9-84f4-3ddc12600334"),
            emoji="😀",
        ),
        "sticker",
    ),
)


@pytest.mark.parametrize(
    "api_attachment,domain_attachment,attr_name",
    API_AND_DOMAIN_NON_FILE_ATTACHMENTS,
)
async def test__async_execute_raw_bot_command__non_file_attachments_types(
    api_attachment: Dict[str, Any],
    domain_attachment: IncomingAttachment,
    attr_name: str,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(body="😀", attachment=api_attachment)

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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

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
                "content": "data:audio/mp3;base64,SGVsbG8sIHdvcmxkIQo=",
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
    (
        {
            "data": {
                "content": "data:audio/m4a;base64,SGVsbG8sIHdvcmxkIQo=",
                "duration": 10,
            },
            "type": "voice",
        },
        AttachmentVoice(
            type=AttachmentTypes.VOICE,
            filename="record.m4a",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
            duration=10,
        ),
    ),
)


@pytest.mark.parametrize(
    "api_attachment,domain_attachment",
    API_AND_DOMAIN_FILE_ATTACHMENTS,
)
async def test__async_execute_raw_bot_command__file_attachments_types(
    api_attachment: Dict[str, Any],
    domain_attachment: IncomingAttachment,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(attachment=api_attachment)

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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message
    assert incoming_message.file == domain_attachment


async def test__async_execute_raw_bot_command__unknown_attachment_type(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    unknown_attachment = {"data": {"foo": "bar"}, "type": "baz"}
    payload = api_incoming_message_factory(attachment=unknown_attachment)

    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert "Received unknown attachment type" in loguru_caplog.text


async def test__async_execute_raw_bot_command__empty_attachment(
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    empty_attachment = {
        "data": {
            "content": "",
            "file_name": "empty_file.txt",
        },
        "type": "document",
    }
    payload = api_incoming_message_factory(attachment=empty_attachment)

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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message
    assert incoming_message.file == AttachmentDocument(
        type=AttachmentTypes.DOCUMENT,
        filename="empty_file.txt",
        size=0,
        is_async_file=False,
        content=b"",
    )
