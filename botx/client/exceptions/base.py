import httpx

from botx.bot.models.method_callbacks import BotAPIMethodFailedCallback


class BaseClientException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    @classmethod
    def from_response(cls, response: httpx.Response) -> "BaseClientException":
        method = response.request.method
        url = response.request.url
        status_code = response.status_code
        content = response.content

        message = (
            f"{method} {url}\n"  # noqa: WPS221 (Strange error on CI)
            f"failed with code {status_code} and payload:\n"
            f"{content!r}"
        )
        return cls(message)

    @classmethod
    def from_callback(
        cls,
        callback: BotAPIMethodFailedCallback,
    ) -> "BaseClientException":
        message = (
            f"BotX method call with sync_id `{callback.sync_id!s}` "
            f"failed with: {callback}"
        )
        return cls(message)
