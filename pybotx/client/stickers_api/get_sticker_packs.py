from typing import List, Literal, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.stickers import StickerPackFromList, StickerPackPage


class BotXAPIGetStickerPacksRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    limit: int
    after: Optional[str]

    @classmethod
    def from_domain(
        cls,
        huid: UUID,
        limit: int,
        after: Optional[str],
    ) -> "BotXAPIGetStickerPacksRequestPayload":
        return cls(user_huid=huid, limit=limit, after=after if after else Undefined)


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
            sticker_packs=[
                StickerPackFromList(
                    id=sticker_pack.id,
                    name=sticker_pack.name,
                    is_public=sticker_pack.public,
                    stickers_count=sticker_pack.stickers_count,
                    sticker_ids=sticker_pack.stickers_order,
                )
                for sticker_pack in self.result.packs
            ],
            after=self.result.pagination.after,
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
