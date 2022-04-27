from typing import Literal, NoReturn
from uuid import UUID

import httpx

from pybotx.async_buffer import AsyncBufferReadable
from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.exceptions.http import InvalidBotXStatusCodeError
from pybotx.client.stickers_api.exceptions import (
    InvalidEmojiError,
    InvalidImageError,
    StickerPackOrStickerNotFoundError,
)
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.attachments import encode_rfc2397
from pybotx.models.stickers import Sticker


class BotXAPIAddStickerRequestPayload(UnverifiedPayloadBaseModel):
    sticker_pack_id: UUID
    emoji: str
    image: str

    @classmethod
    async def from_domain(
        cls,
        sticker_pack_id: UUID,
        emoji: str,
        async_buffer: AsyncBufferReadable,
    ) -> "BotXAPIAddStickerRequestPayload":
        mimetype = "image/png"

        content = await async_buffer.read()
        b64_content = encode_rfc2397(content, mimetype)

        return cls(sticker_pack_id=sticker_pack_id, emoji=emoji, image=b64_content)


class BotXAPIAddStickerResult(VerifiedPayloadBaseModel):
    id: UUID
    emoji: str
    link: str


class BotXAPIAddStickerResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIAddStickerResult

    def to_domain(self, pack_id: UUID) -> Sticker:
        return Sticker(
            id=self.result.id,
            emoji=self.result.emoji,
            image_link=self.result.link,
            pack_id=pack_id,
        )


def bad_request_error_handler(response: httpx.Response) -> NoReturn:  # noqa: WPS238
    reason = response.json().get("reason")

    if reason == "pack_not_found":
        raise StickerPackOrStickerNotFoundError.from_response(response)

    error_data = response.json().get("error_data")

    if error_data.get("emoji") == "invalid":
        raise InvalidEmojiError.from_response(response)
    elif error_data.get("image") == "invalid":
        raise InvalidImageError.from_response(response)

    raise InvalidBotXStatusCodeError(response)


class AddStickerMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        400: bad_request_error_handler,
    }

    async def execute(
        self,
        payload: BotXAPIAddStickerRequestPayload,
    ) -> BotXAPIAddStickerResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        sticker_pack_id = jsonable_dict.pop("sticker_pack_id")

        path = f"/api/v3/botx/stickers/packs/{sticker_pack_id}/stickers"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=jsonable_dict,
        )

        return self._verify_and_extract_api_model(
            BotXAPIAddStickerResponsePayload,
            response,
        )
