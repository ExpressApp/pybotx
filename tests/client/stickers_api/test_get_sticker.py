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
from pybotx.models.stickers import Sticker

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__get_sticker__sticker_pack_or_sticker_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/"
        f"stickers/75bb24c9-7c08-5db0-ae3e-085929e80c54",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "error_data": {
                    "pack_id": "26080153-a57d-5a8c-af0e-fdecee3c4435",
                    "sticker_id": "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                },
                "errors": ["Sticker or sticker pack not found."],
                "reason": "not_found",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.get_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                sticker_id=UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
            )

    # - Assert -
    assert "not_found" in str(exc.value)
    assert endpoint.called


async def test__get_sticker__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/"
        f"stickers/75bb24c9-7c08-5db0-ae3e-085929e80c54",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                    "emoji": "🤔",
                    "link": "https://cts-host/uploads/sticker_pack/image.png",
                    "preview": "https://cts-host/uploads/sticker_pack/image.png",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sticker = await bot.get_sticker(
            bot_id=bot_id,
            sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
            sticker_id=UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
        )

    # - Assert -
    assert sticker == Sticker(
        id=UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
        emoji="🤔",
        image_link="https://cts-host/uploads/sticker_pack/image.png",
    )

    assert endpoint.called
