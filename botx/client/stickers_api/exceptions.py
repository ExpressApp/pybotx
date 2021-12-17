from botx.client.exceptions.base import BaseClientException


class StickerPackNotFoundError(BaseClientException):
    """Sticker pack with specified sticker_pack_id not found."""


class StickerNotFoundError(BaseClientException):
    """Sticker with specified sticker_id not found."""


class InvalidEmojiError(BaseClientException):
    """Bad emoji."""


class InvalidImageError(BaseClientException):
    """Bad image."""
