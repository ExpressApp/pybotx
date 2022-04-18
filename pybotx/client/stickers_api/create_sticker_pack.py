from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.stickers import StickerPack


class BotXAPICreateStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    name: str
    user_huid: Missing[UUID]

    @classmethod
    def from_domain(
        cls,
        name: str,
        huid: Missing[UUID],
    ) -> "BotXAPICreateStickerPackRequestPayload":
        return cls(name=name, user_huid=huid)


class BotXAPICreateStickerPackResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    public: bool


class BotXAPICreateStickerPackResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPICreateStickerPackResult

    def to_domain(self) -> StickerPack:
        return StickerPack(
            id=self.result.id,
            name=self.result.name,
            is_public=self.result.public,
            stickers=[],
        )


class CreateStickerPackMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
    }

    async def execute(
        self,
        payload: BotXAPICreateStickerPackRequestPayload,
    ) -> BotXAPICreateStickerPackResponsePayload:
        path = "/api/v3/botx/stickers/packs"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPICreateStickerPackResponsePayload,
            response,
        )
