from typing import List, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
from pybotx.client.stickers_api.sticker_pack import BotXAPIGetStickerPackResponsePayload
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPIEditStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID
    name: str
    preview: UUID
    stickers_order: Optional[List[UUID]]

    @classmethod
    def from_domain(
        cls,
        sticker_pack_id: UUID,
        name: str,
        preview: UUID,
        stickers_order: Optional[List[UUID]],
    ) -> "BotXAPIEditStickerPackRequestPayload":
        return cls(
            sticker_pack_id=sticker_pack_id,
            name=name,
            preview=preview,
            stickers_order=stickers_order,
        )


class EditStickerPackMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackOrStickerNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIEditStickerPackRequestPayload,
    ) -> BotXAPIGetStickerPackResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        sticker_pack_id = jsonable_dict.pop("sticker_pack_id")

        path = f"/api/v3/botx/stickers/packs/{sticker_pack_id}"

        response = await self._botx_method_call(
            "PUT",
            self._build_url(path),
            json=jsonable_dict,
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetStickerPackResponsePayload,
            response,
        )
