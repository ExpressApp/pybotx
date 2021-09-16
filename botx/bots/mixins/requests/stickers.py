"""Mixin for shortcut for users resource requests."""

from typing import List, Optional, Tuple
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.stickers.add_sticker import AddSticker
from botx.clients.methods.v3.stickers.create_sticker_pack import CreateStickerPack
from botx.clients.methods.v3.stickers.delete_sticker import DeleteSticker
from botx.clients.methods.v3.stickers.delete_sticker_pack import DeleteStickerPack
from botx.clients.methods.v3.stickers.edit_sticker_pack import EditStickerPack
from botx.clients.methods.v3.stickers.sticker import GetSticker
from botx.clients.methods.v3.stickers.sticker_pack import GetStickerPack
from botx.clients.methods.v3.stickers.sticker_pack_list import GetStickerPackList
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.stickers import (
    Sticker,
    StickerFromPack,
    StickerPack,
    StickerPackList,
    StickerPackPreview,
)


class StickersMixin:  # noqa: WPS214
    """Mixin for shortcut for users resource requests."""

    async def get_sticker_pack_list(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        user_huid: Optional[UUID] = None,
        limit: int = 1,
        after: Optional[str] = None,
    ) -> Tuple[List[StickerPackPreview], Optional[str]]:
        """Get sticker pack list.

        Arguments:
            credentials: credentials for making request.
            user_huid: author HUID.
            limit: returning value count.
            after: cursor hash for pagination.

        Returns:
            Sticker packs list and cursor.
        """
        response: StickerPackList = await self.call_method(
            GetStickerPackList(user_huid=user_huid, limit=limit, after=after),
            credentials=credentials,
        )

        return response.packs, response.pagination.after

    async def get_sticker_pack(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
    ) -> StickerPack:
        """Get sticker pack.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.

        Returns:
            StickerPack entity.
        """
        return await self.call_method(
            GetStickerPack(pack_id=pack_id),
            credentials=credentials,
        )

    async def get_sticker_from_pack(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
        sticker_id: UUID,
    ) -> StickerFromPack:
        """Get sticker from pack.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.
            sticker_id: sticker ID.

        Returns:
            StickerFromPack entity.
        """
        return await self.call_method(
            GetSticker(pack_id=pack_id, sticker_id=sticker_id),
            credentials=credentials,
        )

    async def create_sticker_pack(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        name: str,
        user_huid: UUID,
    ) -> StickerPack:
        """Create sticker pack.

        Arguments:
            credentials: credentials for making request.
            name: sticker pack name.
            user_huid: author HUID.

        Returns:
            StickerPackPreview entity.
        """
        return await self.call_method(
            CreateStickerPack(name=name, user_huid=user_huid),
            credentials=credentials,
        )

    async def add_sticker(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
        emoji: str,
        image: str,
    ) -> Sticker:
        """Add sticker.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.
            emoji: emoji that the sticker will be associated with.
            image: sticker image.

        Returns:
            Sticker entity.
        """
        return await self.call_method(
            AddSticker(pack_id=pack_id, emoji=emoji, image=image),
            credentials=credentials,
        )

    async def edit_sticker_pack(  # noqa: WPS211
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
        name: str,
        preview: Optional[UUID] = None,
        stickers_order: Optional[List[UUID]] = None,
    ) -> StickerPack:
        """Edit sticker pack.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.
            name: sticker pack name.
            preview: sticker pack preview.
            stickers_order: stickers order in sticker pack.

        Returns:
            StickerPack entity.
        """
        return await self.call_method(
            EditStickerPack(
                pack_id=pack_id,
                name=name,
                preview=preview,
                stickers_order=stickers_order,
            ),
            credentials=credentials,
        )

    async def delete_sticker_pack(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
    ) -> None:
        """Delete sticker pack.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.
        """
        await self.call_method(
            DeleteStickerPack(pack_id=pack_id),
            credentials=credentials,
        )

    async def delete_sticker(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        pack_id: UUID,
        sticker_id: UUID,
    ) -> None:
        """Delete sticker.

        Arguments:
            credentials: credentials for making request.
            pack_id: sticker pack ID.
            sticker_id: sticker ID.
        """
        await self.call_method(
            DeleteSticker(pack_id=pack_id, sticker_id=sticker_id),
            credentials=credentials,
        )
