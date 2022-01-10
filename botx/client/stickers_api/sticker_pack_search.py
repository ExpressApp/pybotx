from typing import List, Optional
from uuid import UUID

from typing_extensions import Literal  # For python 3.7 support

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.stickers import Sticker, StickerPack


class BotXAPISearchStickerResult(VerifiedPayloadBaseModel):
    id: UUID
    emoji: str
    link: str


class BotXAPISearchStickerPackResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    public: bool
    stickers_order: Optional[List[UUID]]
    stickers: List[BotXAPISearchStickerResult]


class BotXAPIGetStickerPackResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISearchStickerPackResult

    def to_domain(self) -> StickerPack:
        return StickerPack(
            id=self.result.id,
            name=self.result.name,
            is_public=self.result.public,
            stickers=[
                Sticker(id=sticker.id, emoji=sticker.emoji, image_link=sticker.link)
                for sticker in self.result.stickers
            ],
        )
