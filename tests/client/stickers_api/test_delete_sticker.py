from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    InvalidBotXStatusCodeError,
    StickerPackOrStickerNotFoundError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__delete_sticker__sticker_or_pack_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.delete(
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

    build_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

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


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__delete_sticker__unexpected_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/78f9743c-8b24-4e97-8059-70908604a252/"
        f"stickers/6ead1e00-f788-4ce6-9e1a-95abe219414e",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "some_reason",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXStatusCodeError) as exc:
            await bot.delete_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("78f9743c-8b24-4e97-8059-70908604a252"),
                sticker_id=UUID("6ead1e00-f788-4ce6-9e1a-95abe219414e"),
            )

    # - Assert -
    assert "some_reason" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__delete_sticker__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.delete(
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.delete_sticker(
            bot_id=bot_id,
            sticker_id=UUID("6ead1e00-f788-4ce6-9e1a-95abe219414e"),
            sticker_pack_id=UUID("78f9743c-8b24-4e97-8059-70908604a252"),
        )

    # - Assert -
    assert endpoint.called
