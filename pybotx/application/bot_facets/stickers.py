from __future__ import annotations

from collections.abc import AsyncIterable
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.stickers import Sticker, StickerPack, StickerPackFromList
from pybotx.domain.ports.async_buffer import AsyncBufferReadable


class BotStickersMixin:
    async def create_sticker_pack(
        self,
        *,
        bot_id: UUID,
        name: str,
        huid: Missing[UUID] = Undefined,
    ) -> StickerPack:
        """Create empty sticker pack.

        :param bot_id: Bot which should perform the request.
        :param name: Sticker pack name.
        :param huid: Sticker pack creator.

        :return: Created sticker pack.
        """
        return await self._botx_api.create_sticker_pack(
            bot_id=bot_id,
            name=name,
            huid=huid,
        )

    async def add_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        emoji: str,
        async_buffer: AsyncBufferReadable,
    ) -> Sticker:
        """Add sticker in sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id to indicate where to add.
        :param emoji: Sticker emoji.
        :param async_buffer: Sticker image file. Only PNG.

        :return: Added sticker.
        """
        return await self._botx_api.add_sticker(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
            emoji=emoji,
            async_buffer=async_buffer,
        )

    async def delete_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> None:
        """Delete sticker from sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Target sticker pack id.
        :param sticker_id: Sticker id which should be deleted.
        """
        await self._botx_api.delete_sticker(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
            sticker_id=sticker_id,
        )

    async def iterate_by_sticker_packs(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
    ) -> AsyncIterable[StickerPackFromList]:
        """Iterate by user sticker packs.

        :param bot_id: Bot which should perform the request.
        :param user_huid: User huid.

        :yield: Sticker pack.
        """
        from pybotx.application import bot as bot_module

        after = None
        limit = bot_module.STICKER_PACKS_PER_PAGE

        while True:
            sticker_pack_page = await self._botx_api.get_sticker_packs(
                bot_id=bot_id,
                user_huid=user_huid,
                limit=limit,
                after=after,
            )
            after = sticker_pack_page.after

            for sticker_pack in sticker_pack_page.sticker_packs:
                yield sticker_pack

            if not after:
                break

    async def get_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> StickerPack:
        """Get sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.

        :return: Sticker pack.
        """
        return await self._botx_api.get_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
        )

    async def delete_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> None:
        """Delete existing sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Target sticker pack.
        """
        await self._botx_api.delete_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
        )

    async def get_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> Sticker:
        """Get sticker.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.
        :param sticker_id: Sticker id.

        :return: Sticker.
        """
        return await self._botx_api.get_sticker(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
            sticker_id=sticker_id,
        )

    async def edit_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        name: str,
        preview: UUID,
        stickers_order: list[UUID],
    ) -> StickerPack:
        """Edit Sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.
        :param name: Sticker pack name.
        :param preview: Sticker from the set selected as a preview.
        :param stickers_order: Sticker IDs in order they are displayed.

        :return: Edited sticker pack.
        """
        return await self._botx_api.edit_sticker_pack(
            bot_id=bot_id,
            sticker_pack_id=sticker_pack_id,
            name=name,
            preview=preview,
            stickers_order=stickers_order,
        )
