from uuid import uuid4

import pytest

from botx.clients.methods.v3.stickers.add_sticker import AddSticker
from botx.clients.methods.v3.stickers.create_sticker_pack import CreateStickerPack
from botx.clients.methods.v3.stickers.delete_sticker import DeleteSticker
from botx.clients.methods.v3.stickers.delete_sticker_pack import DeleteStickerPack
from botx.clients.methods.v3.stickers.edit_sticker_pack import EditStickerPack
from botx.clients.methods.v3.stickers.sticker import GetSticker
from botx.clients.methods.v3.stickers.sticker_pack import GetStickerPack
from botx.clients.methods.v3.stickers.sticker_pack_list import GetStickerPackList
from botx.testing.content import PNG_DATA

pytestmark = pytest.mark.asyncio


async def test_get_sticker_pack_list(client, message):
    await client.bot.get_sticker_pack_list(message.credentials)
    assert isinstance(client.requests[0], GetStickerPackList)


async def test_get_sticker_pack(client, message):
    await client.bot.get_sticker_pack(message.credentials, pack_id=uuid4())
    assert isinstance(client.requests[0], GetStickerPack)


async def test_get_sticker_from_pack(client, message):
    await client.bot.get_sticker_from_pack(
        message.credentials,
        pack_id=uuid4(),
        sticker_id=uuid4(),
    )
    assert isinstance(client.requests[0], GetSticker)


async def test_create_sticker_pack(client, message):
    await client.bot.create_sticker_pack(
        message.credentials,
        name="Test sticker pack",
        user_huid=uuid4(),
    )
    assert isinstance(client.requests[0], CreateStickerPack)


async def test_add_sticker_into_pack(client, message):
    await client.bot.add_sticker(
        message.credentials,
        pack_id=uuid4(),
        emoji="🐢",
        image=PNG_DATA,
    )
    assert isinstance(client.requests[0], AddSticker)


async def test_edit_sticker_pack(client, message):
    await client.bot.edit_sticker_pack(
        message.credentials,
        pack_id=uuid4(),
        name="New test sticker pack",
    )
    assert isinstance(client.requests[0], EditStickerPack)


async def test_delete_sticker_pack(client, message):
    await client.bot.delete_sticker_pack(message.credentials, pack_id=uuid4())
    assert isinstance(client.requests[0], DeleteStickerPack)


async def test_delete_sticker_from_pack(client, message):
    await client.bot.delete_sticker(
        message.credentials,
        pack_id=uuid4(),
        sticker_id=uuid4(),
    )
    assert isinstance(client.requests[0], DeleteSticker)
