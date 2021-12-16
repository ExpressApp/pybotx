from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from botx.async_buffer import AsyncBufferWritable
from botx.bot.contextvars import bot_var


@dataclass
class Sticker:
    """Sticker from sticker pack.

    Attributes:
        id: Sticker id.
        emoji: Sticker emoji.
        link: Sticker image link.

    """

    id: UUID
    emoji: str
    image_link: str

    async def download(
        self,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        bot = bot_var.get()

        response = await bot._httpx_client.get(self.image_link)  # noqa: WPS437
        response.raise_for_status()

        await async_buffer.write(response.content)

        await async_buffer.seek(0)


@dataclass
class StickerPack:
    """Sticker pack.

    Attributes:
        id: Sticker pack id.
        name: Sticker pack name.
        is_public: Is public pack.
        stickers_order: Stickers order.
        stickers: Stickers data.

    """

    id: UUID
    name: str
    is_public: bool
    stickers_order: Optional[List[UUID]]
    stickers: List[Sticker]


@dataclass
class StickerPackFromList:
    """Sticker pack from list.

    Attributes:
        id: Sticker pack id.
        name: Sticker pack name.
        is_public: Is public pack
        stickers_count: Stickers count in pack
        stickers_ids: Stickers ids in pack

    """

    id: UUID
    name: str
    is_public: bool
    stickers_count: int
    stickers_ids: Optional[List[UUID]]


@dataclass
class StickerPackPage:
    """Sticker pack page.

    Attributes:
        sticker_packs: Sticker pack list.
        after: Base64 string for pagination.

    """

    sticker_packs: List[StickerPackFromList]
    after: Optional[str]
