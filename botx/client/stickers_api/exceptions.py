from botx.client.exceptions.base import BaseClientException


class StickerPackNotFoundError(BaseClientException):
    """Chat with specified sticker_pack_id not found."""


class InvalidEmojiError(BaseClientException):
    """Bad emoji."""


class InvalidImageError(BaseClientException):
    """Bad image."""
