import httpx


class ExceptionNotRaisedInStatusHandlerError(Exception):
    def __init__(self, status_code: int, status_handler_name: str) -> None:
        self.status_code = status_code
        self.status_handler_name = status_handler_name

        self.message = (
            f"`{status_handler_name}` should raise exception "
            f"for status code {status_code}"
        )
        super().__init__(self.message)


class BaseBotXAPIError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.method = response.request.method
        self.url = response.request.url
        self.status_code = response.status_code
        self.content = response.content

        self.message = (
            f"{self.method} {self.url}\n"  # noqa: WPS221 (Strange error on CI)
            f"failed with code {self.status_code} and payload:\n"
            f"{self.content!r}"
        )
        super().__init__(self.message)


class InvalidBotXStatusCodeError(BaseBotXAPIError):
    """Received invalid status code."""


class InvalidBotXResponseError(BaseBotXAPIError):
    """Received invalid response."""


class InvalidBotCredentialsError(BaseBotXAPIError):
    """Can't get token with current credentials."""
