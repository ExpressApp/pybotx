from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


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
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(StickerPackOrStickerNotFoundError),
    }

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
