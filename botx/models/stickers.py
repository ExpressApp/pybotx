from dataclasses import dataclass
from typing import List
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
        is_public:
        stickers: Stickers data.

    """

    id: UUID
    name: str
    is_public: bool
    stickers: List[Sticker]
