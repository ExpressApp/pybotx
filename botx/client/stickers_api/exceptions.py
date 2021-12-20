from botx.client.exceptions.base import BaseClientError


class StickerPackNotFoundError(BaseClientError):
    """Sticker pack with specified sticker_pack_id not found."""


class StickerNotFoundError(BaseClientError):
    """Sticker with specified sticker_id not found."""


class InvalidEmojiError(BaseClientError):
    """Bad emoji."""


class InvalidImageError(BaseClientError):
    """Bad image."""
