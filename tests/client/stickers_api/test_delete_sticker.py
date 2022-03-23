from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    StickerPackOrStickerNotFoundError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__delete_sticker__sticker_or_pack_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/78f9743c-8b24-4e97-8059-70908604a252/"
        f"stickers/6ead1e00-f788-4ce6-9e1a-95abe219414e",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "error_data": {
                    "pack_id": "78f9743c-8b24-4e97-8059-70908604a252",
                    "sticker_id": "6ead1e00-f788-4ce6-9e1a-95abe219414e",
                },
                "errors": ["Sticker or sticker pack not found."],
                "reason": "not_found",
                "status": "error",
            },
        ),
    )

    build_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(build_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.delete_sticker(
                bot_id=bot_id,
                sticker_id=UUID("6ead1e00-f788-4ce6-9e1a-95abe219414e"),
                sticker_pack_id=UUID("78f9743c-8b24-4e97-8059-70908604a252"),
            )

        # - Assert -
        assert "Sticker or sticker pack not found" in str(exc.value)
        assert endpoint.called


async def test__delete_sticker__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/78f9743c-8b24-4e97-8059-70908604a252/"
        f"stickers/6ead1e00-f788-4ce6-9e1a-95abe219414e",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "delete_sticker_from_pack_pushed",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.delete_sticker(
            bot_id=bot_id,
            sticker_id=UUID("6ead1e00-f788-4ce6-9e1a-95abe219414e"),
            sticker_pack_id=UUID("78f9743c-8b24-4e97-8059-70908604a252"),
        )

    # - Assert -
    assert endpoint.called
