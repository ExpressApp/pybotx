from uuid import UUID

from typing_extensions import Literal  # For python 3.7 support

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIDeleteStickerRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID
    sticker_id: UUID

    @classmethod
    async def from_domain(
        cls,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> "BotXAPIDeleteStickerRequestPayload":
        return cls(sticker_pack_id=sticker_pack_id, sticker_id=sticker_id)


class BotXAPIDeleteStickerResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class DeleteStickerMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIDeleteStickerRequestPayload,
    ) -> None:
        path = (
            f"/api/v3/botx/stickers/packs/{payload.sticker_pack_id}"
            f"/stickers/{payload.sticker_id}"
        )

        response = await self._botx_method_call(
            "DELETE",
            self._build_url(path),
        )

        self._verify_and_extract_api_model(
            BotXAPIDeleteStickerResponsePayload,
            response,
        )
