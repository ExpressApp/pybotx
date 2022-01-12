from uuid import UUID

from typing_extensions import Literal  # For python 3.7 support

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIDeleteStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID

    @classmethod
    def from_domain(
        cls,
        sticker_pack_id: UUID,
    ) -> "BotXAPIDeleteStickerPackRequestPayload":
        return cls(sticker_pack_id=sticker_pack_id)


class BotXAPIDeleteStickerPackResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class DeleteStickerPackMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackOrStickerNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIDeleteStickerPackRequestPayload,
    ) -> BotXAPIDeleteStickerPackResponsePayload:
        path = f"/api/v3/botx/stickers/packs/{payload.sticker_pack_id}"

        response = await self._botx_method_call(
            "DELETE",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIDeleteStickerPackResponsePayload,
            response,
        )