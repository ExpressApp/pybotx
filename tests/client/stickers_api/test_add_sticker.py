from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    InvalidBotXStatusCodeError,
    InvalidEmojiError,
    InvalidImageError,
    Sticker,
    StickerPackOrStickerNotFoundError,
    lifespan_wrapper,
)

PNG_IMAGE = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00"
    b"\x00\x00%\xdbV\xca\x00\x00\x00\x03PLTE\x00\x00\x00\xa7z=\xda\x00"
    b"\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\nIDAT\x08\xd7c`\x00"
    b"\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
)
PNG_IMAGE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3a"
    "AAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII="
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__add_sticker__is_not_png_error_raised(
    respx_mock: MockRouter,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(b"Hello, world!\n")
    await async_buffer.seek(0)

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "Passed file is not PNG" in str(exc.value)


async def test__add_sticker__bad_file_size_error_raised(
    respx_mock: MockRouter,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE + b"\x00" * (512 * 1024 + 1))
    await async_buffer.seek(0)

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "Passed file size is greater than 0.5 Mb" in str(exc.value)


async def test__add_sticker__unexpected_bad_request_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE)
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/stickers",
        headers={"Authorization": "Bearer token"},
        json={"emoji": "🤔", "image": f"data:image/png;base64,{PNG_IMAGE_B64}"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "some_reason",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXStatusCodeError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "some_reason" in str(exc.value)
    assert endpoint.called


async def test__add_sticker__sticker_pack_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE)
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/stickers",
        headers={"Authorization": "Bearer token"},
        json={"emoji": "🤔", "image": f"data:image/png;base64,{PNG_IMAGE_B64}"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "error_data": {"pack_id": "26080153-a57d-5a8c-af0e-fdecee3c4435"},
                "errors": ["Failed to add sticker because pack not found."],
                "reason": "pack_not_found",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(StickerPackOrStickerNotFoundError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "pack_not_found" in str(exc.value)
    assert endpoint.called


async def test__add_sticker__invalid_emoji_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE)
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/stickers",
        headers={"Authorization": "Bearer token"},
        json={"emoji": "🤔", "image": f"data:image/png;base64,{PNG_IMAGE_B64}"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "error_data": {"emoji": "invalid"},
                "errors": [],
                "reason": "malformed_request",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidEmojiError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "malformed_request" in str(exc.value)
    assert endpoint.called


async def test__add_sticker__invalid_image_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE)
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/stickers",
        headers={"Authorization": "Bearer token"},
        json={"emoji": "🤔", "image": f"data:image/png;base64,{PNG_IMAGE_B64}"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "error_data": {"image": "invalid"},
                "errors": [],
                "reason": "malformed_request",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidImageError) as exc:
            await bot.add_sticker(
                bot_id=bot_id,
                sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
                emoji="🤔",
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "malformed_request" in str(exc.value)
    assert endpoint.called


async def test__add_sticker__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(PNG_IMAGE)
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/stickers/packs/26080153-a57d-5a8c-af0e-fdecee3c4435/stickers",
        headers={"Authorization": "Bearer token"},
        json={"emoji": "🤔", "image": f"data:image/png;base64,{PNG_IMAGE_B64}"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": "75bb24c9-7c08-5db0-ae3e-085929e80c54",
                    "emoji": "🤔",
                    "link": "http://cts-domain/uploads/sticker_pack/26080153-a57d-5a8c-af0e-fdecee3c4435/b4577728162f4d9ea2b35f25f9f0dcde.png?v=1626137130775",
                    "inserted_at": "2020-12-28T12:56:43.672163Z",
                    "updated_at": "2020-12-28T12:56:43.672163Z",
                    "deleted_at": None,
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sticker = await bot.add_sticker(
            bot_id=bot_id,
            sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
            emoji="🤔",
            async_buffer=async_buffer,
        )

    # - Assert -
    assert sticker == Sticker(
        id=UUID("75bb24c9-7c08-5db0-ae3e-085929e80c54"),
        emoji="🤔",
        image_link="http://cts-domain/uploads/sticker_pack/26080153-a57d-5a8c-af0e-fdecee3c4435/b4577728162f4d9ea2b35f25f9f0dcde.png?v=1626137130775",
        pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
    )

    assert endpoint.called
