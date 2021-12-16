from typing import List, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.stickers import StickerPackFromList, StickerPackPage

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIGetStickerPacksRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    limit: int
    after: Optional[str]

    @classmethod
    def from_domain(
        cls,
        user_huid: UUID,
        limit: int,
        after: Optional[str],
    ) -> "BotXAPIGetStickerPacksRequestPayload":
        return cls(user_huid=user_huid, limit=limit, after=after)


class BotXAPIGetPaginationResult(VerifiedPayloadBaseModel):
    after: Optional[str]


class BotXAPIGetStickerPackResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    public: bool
    stickers_count: int
    stickers_order: Optional[List[UUID]]


class BotXAPIGetStickerPacksResult(VerifiedPayloadBaseModel):
    packs: List[BotXAPIGetStickerPackResult]
    pagination: BotXAPIGetPaginationResult


class BotXAPIGetStickerPacksResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIGetStickerPacksResult

    def to_domain(self) -> StickerPackPage:
        return StickerPackPage(
            [
                StickerPackFromList(
                    id=sticker_pack.id,
                    name=sticker_pack.name,
                    is_public=sticker_pack.public,
                    stickers_count=sticker_pack.stickers_count,
                    stickers_ids=sticker_pack.stickers_order,
                )
                for sticker_pack in self.result.packs
            ],
            self.result.pagination.after,
        )


class GetStickerPacksMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIGetStickerPacksRequestPayload,
    ) -> BotXAPIGetStickerPacksResponsePayload:
        path = "/api/v3/botx/stickers/packs"
        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetStickerPacksResponsePayload,
            response,
        )
