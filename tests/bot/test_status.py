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
async def test_hidden_command_not_in_menu(
    status_recipient: StatusRecipient,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    wrong_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_visible_command_in_menu(
    status_recipient: StatusRecipient,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    wrong_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_command_not_in_menu_if_visible_func_return_false(
    status_recipient: StatusRecipient,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    async def visible_func(status_recipient: StatusRecipient, bot: Bot) -> bool:
        return False

    @collector.command("/command", visible=visible_func, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    wrong_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_command_in_menu_if_visible_func_return_true(
    status_recipient: StatusRecipient,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    async def visible_func(status_recipient: StatusRecipient, bot: Bot) -> bool:
        return True

    @collector.command("/command", visible=visible_func, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    wrong_handler_trigger.assert_not_called()
