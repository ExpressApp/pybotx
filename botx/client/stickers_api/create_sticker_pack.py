from datetime import datetime as dt
from typing import Any, List, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.stickers import StickerPack

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPICreateStickerPackRequestPayload(UnverifiedPayloadBaseModel):
    name: str

    @classmethod
    def from_domain(cls, name: str) -> "BotXAPICreateStickerPackRequestPayload":
        return cls(name=name)


class BotXAPICreateStickerPackResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    public: bool
    preview: Optional[str]
    stickers: List[Any]
    stickers_order: List[UUID]
    inserted_at: dt
    updated_at: dt
    deleted_at: Optional[dt]


class BotXAPICreateStickerPackResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPICreateStickerPackResult

    def to_domain(self) -> StickerPack:
        return StickerPack(
            id=self.result.id,
            name=self.result.name,
            is_public=self.result.public,
            stickers=self.result.stickers,
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
