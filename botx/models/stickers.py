from dataclasses import dataclass
from typing import List
from uuid import UUID


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
