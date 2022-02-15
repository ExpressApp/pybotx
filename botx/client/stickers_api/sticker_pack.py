from typing import List, Literal, Optional
from uuid import UUID

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.stickers import Sticker, StickerPack


class BotXAPIGetStickerResult(VerifiedPayloadBaseModel):
    id: UUID
    emoji: str
    link: str


class BotXAPIGetStickerPackResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    public: bool
    stickers_order: Optional[List[UUID]]
    stickers: List[BotXAPIGetStickerResult]


class BotXAPIGetStickerPackResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIGetStickerPackResult

    def to_domain(self) -> StickerPack:
        if self.result.stickers_order:
            self.result.stickers.sort(
                key=lambda pack: self.result.stickers_order.index(  # type:ignore
                    pack.id,
                ),
            )

        return StickerPack(
            id=self.result.id,
            name=self.result.name,
            is_public=self.result.public,
            stickers=[
                Sticker(id=sticker.id, emoji=sticker.emoji, image_link=sticker.link)
                for sticker in self.result.stickers
            ],
        )
