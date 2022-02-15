from typing import Literal
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.stickers import Sticker


class BotXAPIGetStickerRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID
    sticker_id: UUID

    @classmethod
    def from_domain(
        cls,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> "BotXAPIGetStickerRequestPayload":
        return cls(sticker_pack_id=sticker_pack_id, sticker_id=sticker_id)


class BotXAPIGetStickerResult(VerifiedPayloadBaseModel):
    id: UUID
    emoji: str
    link: str


class BotXAPIGetStickerResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIGetStickerResult

    def to_domain(self) -> Sticker:
        return Sticker(
            id=self.result.id,
            emoji=self.result.emoji,
            image_link=self.result.link,
        )


class GetStickerMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackOrStickerNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIGetStickerRequestPayload,
    ) -> BotXAPIGetStickerResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        path = (
            f"/api/v3/botx/stickers/packs/{jsonable_dict['sticker_pack_id']}/"
            f"stickers/{jsonable_dict['sticker_id']}"
        )

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetStickerResponsePayload,
            response,
        )
