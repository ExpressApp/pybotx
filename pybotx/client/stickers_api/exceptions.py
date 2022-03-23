from pybotx.client.exceptions.base import BaseClientError


class StickerPackOrStickerNotFoundError(BaseClientError):
    """Sticker pack or sticker with specified id not found."""


class InvalidEmojiError(BaseClientError):
    """Bad emoji."""


class InvalidImageError(BaseClientError):
    """Bad image."""
