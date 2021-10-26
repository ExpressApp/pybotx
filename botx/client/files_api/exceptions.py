from botx.client.exceptions.http import InvalidBotXStatusCodeError


class FileDeletedError(InvalidBotXStatusCodeError):
    """File deleted."""
