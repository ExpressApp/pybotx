from typing import List, NoReturn, Optional, Type
from uuid import UUID

import httpx

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import StatusHandler
from botx.client.exceptions.base import BaseClientException
from botx.client.stickers_api.exceptions import StickerPackNotFoundError
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.stickers import Sticker, StickerPack

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


def response_exception_thrower(
    exc: Type[BaseClientException],
    comment: Optional[str] = None,
) -> StatusHandler:
    def factory(response: httpx.Response) -> NoReturn:
        raise exc.from_response(response, comment)

    return factory


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
        return StickerPack(
            id=self.result.id,
            name=self.result.name,
            is_public=self.result.public,
            stickers_order=self.result.stickers_order,
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
        sticker_pack_id = jsonable_dict.pop("sticker_pack_id")
        path = f"/api/v3/botx/stickers/packs/{sticker_pack_id}"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            json=jsonable_dict,
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetStickerPackResponsePayload,
            response,
        )
