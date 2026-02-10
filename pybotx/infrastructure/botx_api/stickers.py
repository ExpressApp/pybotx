from __future__ import annotations

from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.stickers import Sticker, StickerPack, StickerPackPage
from pybotx.domain.ports.async_buffer import AsyncBufferReadable
from pybotx.infrastructure.client.stickers_api.add_sticker import (
    AddStickerMethod,
    BotXAPIAddStickerRequestPayload,
)
from pybotx.infrastructure.client.stickers_api.create_sticker_pack import (
    BotXAPICreateStickerPackRequestPayload,
    CreateStickerPackMethod,
)
from pybotx.infrastructure.client.stickers_api.delete_sticker import (
    BotXAPIDeleteStickerRequestPayload,
    DeleteStickerMethod,
)
from pybotx.infrastructure.client.stickers_api.delete_sticker_pack import (
    BotXAPIDeleteStickerPackRequestPayload,
    DeleteStickerPackMethod,
)
from pybotx.infrastructure.client.stickers_api.edit_sticker_pack import (
    BotXAPIEditStickerPackRequestPayload,
    EditStickerPackMethod,
)
from pybotx.infrastructure.client.stickers_api.get_sticker import (
    BotXAPIGetStickerRequestPayload,
    GetStickerMethod,
)
from pybotx.infrastructure.client.stickers_api.get_sticker_pack import (
    BotXAPIGetStickerPackRequestPayload,
    GetStickerPackMethod,
)
from pybotx.infrastructure.client.stickers_api.get_sticker_packs import (
    BotXAPIGetStickerPacksRequestPayload,
    GetStickerPacksMethod,
)
from pybotx.infrastructure.image_validators import (
    ensure_file_content_is_png,
    ensure_sticker_image_size_valid,
)


class StickersApiMixin:
    async def create_sticker_pack(
        self,
        *,
        bot_id: UUID,
        name: str,
        huid: Missing[UUID] = Undefined,
    ) -> StickerPack:
        method = self._method_factory.build(CreateStickerPackMethod, bot_id=bot_id)
        payload = BotXAPICreateStickerPackRequestPayload.from_domain(
            name=name,
            huid=huid,
        )
        botx_api_sticker_pack = await method.execute(payload)
        return botx_api_sticker_pack.to_domain()

    async def add_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        emoji: str,
        async_buffer: AsyncBufferReadable,
    ) -> Sticker:
        await ensure_file_content_is_png(async_buffer)
        await ensure_sticker_image_size_valid(async_buffer)

        method = self._method_factory.build(AddStickerMethod, bot_id=bot_id)
        payload = await BotXAPIAddStickerRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            emoji=emoji,
            async_buffer=async_buffer,
        )
        botx_api_sticker = await method.execute(payload)
        return botx_api_sticker.to_domain(pack_id=sticker_pack_id)

    async def delete_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> None:
        method = self._method_factory.build(DeleteStickerMethod, bot_id=bot_id)
        payload = await BotXAPIDeleteStickerRequestPayload.from_domain(
            sticker_id=sticker_id,
            sticker_pack_id=sticker_pack_id,
        )
        await method.execute(payload)

    async def get_sticker_packs(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        limit: int,
        after: str | None = None,
    ) -> StickerPackPage:
        method = self._method_factory.build(GetStickerPacksMethod, bot_id=bot_id)
        payload = BotXAPIGetStickerPacksRequestPayload.from_domain(
            huid=user_huid,
            limit=limit,
            after=after,
        )
        botx_api_sticker_pack_list = await method.execute(payload)
        return botx_api_sticker_pack_list.to_domain()

    async def get_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> StickerPack:
        method = self._method_factory.build(GetStickerPackMethod, bot_id=bot_id)
        payload = BotXAPIGetStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
        )
        botx_api_sticker_pack = await method.execute(payload)
        return botx_api_sticker_pack.to_domain()

    async def delete_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> None:
        method = self._method_factory.build(DeleteStickerPackMethod, bot_id=bot_id)
        payload = BotXAPIDeleteStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
        )
        await method.execute(payload)

    async def get_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> Sticker:
        method = self._method_factory.build(GetStickerMethod, bot_id=bot_id)
        payload = BotXAPIGetStickerRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            sticker_id=sticker_id,
        )
        botx_api_sticker = await method.execute(payload)
        return botx_api_sticker.to_domain(pack_id=sticker_pack_id)

    async def edit_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        name: str,
        preview: UUID,
        stickers_order: list[UUID],
    ) -> StickerPack:
        method = self._method_factory.build(EditStickerPackMethod, bot_id=bot_id)
        payload = BotXAPIEditStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            name=name,
            preview=preview,
            stickers_order=stickers_order,
        )
        botx_api_sticker_pack = await method.execute(payload)
        return botx_api_sticker_pack.to_domain()
