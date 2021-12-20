from typing import List, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.stickers_api.exceptions import StickerPackNotFoundError
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.stickers import Sticker, StickerPack

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIGetStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID

    @classmethod
    def from_domain(
        cls,
        sticker_pack_id: UUID,
    ) -> "BotXAPIGetStickerPackRequestPayload":
        return cls(sticker_pack_id=sticker_pack_id)


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


class GetStickerPackMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIGetStickerPackRequestPayload,
    ) -> BotXAPIGetStickerPackResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        path = f"/api/v3/botx/stickers/packs/{jsonable_dict['sticker_pack_id']}"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetStickerPackResponsePayload,
            response,
        )
