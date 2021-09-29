import pytest

from botx import Bot, HandlerCollector, IncomingMessage, lifespan_wrapper


@pytest.mark.asyncio
async def test_invalid_status() -> None:
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
    assert "validation error" in str(exc)


@pytest.mark.asyncio
async def test_minimally_filled_status_recipient_and_hidden_command() -> None:
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
async def test_maximum_filled_status_recipient_and_visible_command() -> None:
    # - Arrange -
    query = {
        "ad_domain": "domain",
        "ad_login": "login",
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "chat_type": "chat",
        "is_admin": "true",
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
