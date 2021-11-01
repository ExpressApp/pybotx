"""Models for stickers."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from botx.models.base import BotXBaseModel


class Pagination(BotXBaseModel):
    """Model of pagination."""

    #: cursor hash
    after: Optional[str]


class Sticker(BotXBaseModel):
    """Model of sticker from request by id."""

    id: UUID
    emoji: str
    link: str
    inserted_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class StickerFromPack(BotXBaseModel):
    """Model of sticker from sticker pack."""

    id: UUID
    emoji: str
    link: str
    preview: str


class StickerPackPreview(BotXBaseModel):
    """Model of sticker pack from pack list."""

    id: UUID
    name: str
    preview: Optional[str]
    public: Optional[bool]
    stickers_count: int
    stickers_order: Optional[List[UUID]]
    inserted_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


class StickerPackList(BotXBaseModel):
    """Full model of sticker pack list response."""

    #: list of sticker packs
    packs: List[StickerPackPreview]

    #: cursor
    pagination: Pagination


class StickerPack(BotXBaseModel):
    """Model of sticker pack from request by id."""

    id: UUID
    name: str
    public: bool
    preview: Optional[str]
    stickers_order: Optional[List[UUID]]
    stickers: List[Sticker]
    inserted_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
