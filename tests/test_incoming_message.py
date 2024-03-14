from datetime import datetime
from typing import Callable, Optional
from uuid import UUID

import pytest

from pybotx import (
    AttachmentTypes,
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    ClientPlatforms,
    Forward,
    HandlerCollector,
    IncomingMessage,
    MentionBuilder,
    MentionList,
    Reply,
    UserDevice,
    UserSender,
    lifespan_wrapper,
)
from pybotx.models.attachments import AttachmentImage

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_execute_raw_bot_command__minimally_filled_incoming_message(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": None,
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "user_udid": None,
            "username": None,
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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message == IncomingMessage(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        sync_id=UUID("6f40a492-4b5f-54f3-87ee-77126d825b51"),
        source_sync_id=None,
        body="/hello",
        data={},
        metadata={},
        sender=UserSender(
            huid=UUID("f16cdc5f-6366-5552-9ecd-c36290ab3d11"),
            udid=None,
            ad_login=None,
            ad_domain=None,
            username=None,
            is_chat_admin=True,
            is_chat_creator=True,
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
        chat=Chat(
            id=UUID("30dc1980-643a-00ad-37fc-7cc10d74e935"),
            type=ChatTypes.PERSONAL_CHAT,
        ),
        raw_command=None,
    )


async def test__async_execute_raw_bot_command__maximum_filled_incoming_message(
    datetime_formatter: Callable[[str], datetime],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
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
                "type": "reply",
                "data": {
                    "source_sync_id": "a7ffba12-8d0a-534e-8896-a0aa2d93a434",
                    "sender": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "body": "все равно документацию никто не читает...",
                    "mentions": [
                        {
                            "mention_type": "contact",
                            "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                            "mention_data": {
                                "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
                                "name": "Вася Иванов",
                                "conn_type": "cts",
                            },
                        },
                    ],
                    "attachment": None,
                    "reply_type": "chat",
                    "source_group_chat_id": "918da23a-1c9a-506e-8a6f-1328f1499ee8",
                    "source_chat_name": "Serious Dev Chat",
                },
            },
            {
                "type": "forward",
                "data": {
                    "group_chat_id": "918da23a-1c9a-506e-8a6f-1328f1499ee8",
                    "sender_huid": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "forward_type": "chat",
                    "source_chat_name": "Simple Chat",
                    "source_sync_id": "a7ffba12-8d0a-534e-8896-a0aa2d93a434",
                    "source_inserted_at": "2020-04-21T22:09:32.178Z",
                },
            },
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
            "user_udid": "2f18d97b-201b-434d-ac1f-3c6d4b066117",
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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message == IncomingMessage(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        sync_id=UUID("6f40a492-4b5f-54f3-87ee-77126d825b51"),
        source_sync_id=UUID("bc3d06ed-7b2e-41ad-99f9-ca28adc2c88d"),
        body="/hello",
        data={"message": "data"},
        metadata={"message": "metadata"},
        sender=UserSender(
            huid=UUID("f16cdc5f-6366-5552-9ecd-c36290ab3d11"),
            udid=UUID("2f18d97b-201b-434d-ac1f-3c6d4b066117"),
            ad_login="login",
            ad_domain="domain",
            username="Ivanov Ivan Ivanovich",
            is_chat_admin=True,
            is_chat_creator=True,
            device=UserDevice(
                manufacturer="Mozilla",
                device_name="Firefox 91.0",
                os="Linux",
                pushes=False,
                timezone="Europe/Moscow",
                permissions={"microphone": True, "notifications": False},
                platform=ClientPlatforms.WEB,
                platform_package_id="ru.unlimitedtech.express",
                app_version="1.21.9",
                locale="en",
            ),
        ),
        chat=Chat(
            id=UUID("30dc1980-643a-00ad-37fc-7cc10d74e935"),
            type=ChatTypes.PERSONAL_CHAT,
        ),
        raw_command=None,
        file=AttachmentImage(
            type=AttachmentTypes.IMAGE,
            filename="test_file.jpg",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
        ),
        mentions=MentionList(
            [
                MentionBuilder.contact(
                    entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                    name="Вася Иванов",
                ),
            ],
        ),
        forward=Forward(
            chat_id=UUID("918da23a-1c9a-506e-8a6f-1328f1499ee8"),
            author_id=UUID("c06a96fa-7881-0bb6-0e0b-0af72fe3683f"),
            sync_id=UUID("a7ffba12-8d0a-534e-8896-a0aa2d93a434"),
        ),
        reply=Reply(
            author_id=UUID("c06a96fa-7881-0bb6-0e0b-0af72fe3683f"),
            sync_id=UUID("a7ffba12-8d0a-534e-8896-a0aa2d93a434"),
            body="все равно документацию никто не читает...",
            mentions=MentionList(
                [
                    MentionBuilder.contact(
                        entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                        name="Вася Иванов",
                    ),
                ],
            ),
        ),
    )


async def test__async_execute_raw_bot_command__all_mention_types(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
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
            {
                "type": "mention",
                "data": {
                    "mention_type": "user",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {
                        "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
                        "name": "Вася Иванов",
                        "conn_type": "cts",
                    },
                },
            },
            {
                "type": "mention",
                "data": {
                    "mention_type": "channel",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {
                        "group_chat_id": "ab103983-6001-44e9-889e-d55feb295494",
                        "name": "Вася Иванов",
                    },
                },
            },
            {
                "type": "mention",
                "data": {
                    "mention_type": "chat",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {
                        "group_chat_id": "ab103983-6001-44e9-889e-d55feb295494",
                        "name": "Вася Иванов",
                    },
                },
            },
            {
                "type": "mention",
                "data": {
                    "mention_type": "all",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {},
                },
            },
        ],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "user_udid": None,
            "username": None,
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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message
    assert incoming_message.mentions == MentionList(
        [
            MentionBuilder.contact(
                entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
            MentionBuilder.user(
                entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
            MentionBuilder.channel(
                entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
            MentionBuilder.chat(
                entity_id=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
            MentionBuilder.all(),
        ],
    )


async def test__async_execute_raw_bot_command__unknown_entity_type(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [
            {
                "type": "foo",
                "data": {
                    "foo": "bar",
                },
            },
        ],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "user_udid": None,
            "username": None,
        },
        "proto_version": 4,
    }

    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert "Received unknown entity type" in loguru_caplog.text


async def test__async_execute_raw_bot_command__unsupported_chat_type_accepted(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "unsupported_chat_type",
            "device": None,
            "device_meta": None,
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "user_udid": None,
            "username": None,
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
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert incoming_message
    assert incoming_message.chat == Chat(
        id=UUID("30dc1980-643a-00ad-37fc-7cc10d74e935"),
        type="UNSUPPORTED",
    )
