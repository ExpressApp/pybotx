from unittest.mock import Mock
from uuid import uuid4

import pytest

from botx import (
    Bot,
    BotMenu,
    ChatTypes,
    HandlerCollector,
    IncomingMessage,
    StatusRecipient,
    lifespan_wrapper,
)


@pytest.fixture
def status_recipient() -> StatusRecipient:
    return StatusRecipient(
        bot_id=uuid4(),
        huid=uuid4(),
        ad_login=None,
        ad_domain=None,
        is_admin=True,
        chat_type=ChatTypes.PERSONAL_CHAT,
    )


@pytest.mark.asyncio
async def test__get_status__hidden_command_not_in_menu(
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    incorrect_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test__get_status__visible_command_in_menu(
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    incorrect_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test__get_status__command_not_in_menu_if_visible_func_return_false(
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    async def visible_func(status_recipient: StatusRecipient, bot: Bot) -> bool:
        return False

    @collector.command("/command", visible=visible_func, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    incorrect_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test__get_status__command_in_menu_if_visible_func_return_true(
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    async def visible_func(status_recipient: StatusRecipient, bot: Bot) -> bool:
        return True

    @collector.command("/command", visible=visible_func, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    incorrect_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test__raw_get_status__invalid_query() -> None:
    # - Arrange -
    query = {"user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11"}

    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    with pytest.raises(ValueError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            await bot.raw_get_status(query)

    # - Assert -
    assert "validation error" in str(exc.value)


@pytest.mark.asyncio
async def test__raw_get_status__minimally_filled_succeed() -> None:
    # - Arrange -
    query = {
        "bot_id": "34477998-c8c7-53e9-aa4b-66ea5182dc3f",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status


@pytest.mark.asyncio
async def test__raw_get_status__maximum_filled_succeed() -> None:
    # - Arrange -
    query = {
        "ad_domain": "domain",
        "ad_login": "login",
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "chat_type": "chat",
        "is_admin": "true",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status


@pytest.mark.asyncio
async def test__raw_get_status__hidden_command_not_in_status() -> None:
    # - Arrange -
    query = {
        "bot_id": "34477998-c8c7-53e9-aa4b-66ea5182dc3f",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status == {
        "result": {
            "commands": [],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }


@pytest.mark.asyncio
async def test__raw_get_status__visible_command_in_status() -> None:
    # - Arrange -
    query = {
        "bot_id": "34477998-c8c7-53e9-aa4b-66ea5182dc3f",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    collector = HandlerCollector()

    @collector.command("/command", visible=True, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status == {
        "result": {
            "commands": [
                {
                    "body": "/command",
                    "description": "My command",
                    "name": "/command",
                },
            ],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }
