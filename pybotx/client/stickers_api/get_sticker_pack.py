from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
from pybotx.client.stickers_api.sticker_pack import BotXAPIGetStickerPackResponsePayload
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPIGetStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID

    @classmethod
    def from_domain(
        cls,
        sticker_pack_id: UUID,
    ) -> "BotXAPIGetStickerPackRequestPayload":
        return cls(sticker_pack_id=sticker_pack_id)


class GetStickerPackMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackOrStickerNotFoundError),
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
