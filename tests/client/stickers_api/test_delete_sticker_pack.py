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


async def test__delete_sticker_pack__sticker_pack_not_found(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/26080153-a57d-5a8c-af0e-fdecee3c4435",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "error_data": {"pack_id": "26080153-a57d-5a8c-af0e-fdecee3c4435"},
                "errors": ["Sticker pack not found."],
                "reason": "pack_not_found",
                "status": "error",
            },
        ),
    )

    build_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(build_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.delete_sticker_pack(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
            )

        # - Assert -
        assert "pack_not_found" in str(exc)
        assert endpoint.called


async def test__delete_sticker_pack__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/26080153-a57d-5a8c-af0e-fdecee3c4435",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "delete_sticker_pack_pushed",
            },
        ),
    )

    build_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(build_bot) as bot:
        await bot.delete_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
        )

    # - Assert -
    assert endpoint.called
