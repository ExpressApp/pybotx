from typing import NoReturn
from uuid import UUID

import httpx
from typing_extensions import Literal  # for Python 3.7 support

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.exceptions.http import InvalidBotXStatusCodeError
from botx.client.stickers_api.exceptions import StickerPackOrStickerNotFoundError
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


def not_found_error_handler(response: httpx.Response) -> NoReturn:
    reason = response.json().get("reason")

    if reason == "not_found":
        raise StickerPackOrStickerNotFoundError.from_response(response)

    raise InvalidBotXStatusCodeError(response)


class DeleteStickerMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: not_found_error_handler,
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
