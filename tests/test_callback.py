from uuid import UUID

import pytest

from botx import Bot, BotXMethodCallbackNotFound, HandlerCollector, lifespan_wrapper


@pytest.mark.asyncio
async def test__bot__callback_not_found(sync_id: UUID) -> None:
    # - Arrange -
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(BotXMethodCallbackNotFound) as exc:
            bot.set_raw_botx_method_result(
                {
                    "status": "error",
                    "sync_id": str(sync_id),
                    "reason": "chat_not_found",
                    "errors": [],
                    "error_data": {
                        "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
                        "error_description": (
                            "Chat with id 705df263-6bfd-536a-9d51-13524afaab5c not found"
                        ),
                    },
                },
            )

    # - Assert -
    assert "No callback found" in str(exc.value)
