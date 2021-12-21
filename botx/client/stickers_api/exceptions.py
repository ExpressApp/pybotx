from botx.client.exceptions.base import BaseClientError


class StickerPackOrStickerNotFoundError(BaseClientError):
    """Sticker pack or sticker with specified id not found."""


class StickerNotFoundError(BaseClientError):
    """Sticker with specified sticker_id not found."""


class InvalidEmojiError(BaseClientError):
    """Bad emoji."""


class InvalidImageError(BaseClientError):
    """Bad image."""
