from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from botx import (
    Bot,
    BotAccountWithSecret,
    BotMenu,
    ChatTypes,
    HandlerCollector,
    IncomingMessage,
    StatusRecipient,
    UnknownBotAccountError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


@pytest.fixture
def status_recipient(bot_id: UUID) -> StatusRecipient:
    return StatusRecipient(
        bot_id=bot_id,
        huid=uuid4(),
        ad_login=None,
        ad_domain=None,
        is_admin=True,
        chat_type=ChatTypes.PERSONAL_CHAT,
    )


async def test__get_status__hidden_command_not_in_menu(
    bot_account: BotAccountWithSecret,
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    incorrect_handler_trigger.assert_not_called()


async def test__get_status__visible_command_in_menu(
    bot_account: BotAccountWithSecret,
    status_recipient: StatusRecipient,
    incorrect_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    incorrect_handler_trigger.assert_not_called()


async def test__get_status__command_not_in_menu_if_visible_func_return_false(
    bot_account: BotAccountWithSecret,
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

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({})

    incorrect_handler_trigger.assert_not_called()


async def test__get_status__command_in_menu_if_visible_func_return_true(
    bot_account: BotAccountWithSecret,
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

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.get_status(status_recipient)

    # - Assert -
    assert status == BotMenu({"/command": "My command"})

    incorrect_handler_trigger.assert_not_called()


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


async def test__raw_get_status__unknown_bot_account_error_raised() -> None:
    # - Arrange -
    query = {
        "bot_id": "123e4567-e89b-12d3-a456-426655440000",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnknownBotAccountError) as exc:
            await bot.raw_get_status(query)

    # - Assert -
    assert "123e4567-e89b-12d3-a456-426655440000" in str(exc.value)


async def test__raw_get_status__minimally_filled_succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    query = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status


async def test__raw_get_status__minimum_filled_succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    query = {
        "ad_domain": "",
        "ad_login": "",
        "is_admin": "",
        "bot_id": str(bot_id),
        "chat_type": "group_chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status


async def test__raw_get_status__maximum_filled_succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    query = {
        "ad_domain": "domain",
        "ad_login": "login",
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "is_admin": "true",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        status = await bot.raw_get_status(query)

    # - Assert -
    assert status


async def test__raw_get_status__hidden_command_not_in_status(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    query = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    collector = HandlerCollector()

    @collector.command("/_command", visible=False)
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

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


async def test__raw_get_status__visible_command_in_status(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    query = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    collector = HandlerCollector()

    @collector.command("/command", visible=True, description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        pass

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

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
