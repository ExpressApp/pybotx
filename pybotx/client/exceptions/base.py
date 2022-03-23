from typing import Optional

import httpx

from pybotx.models.method_callbacks import BotAPIMethodFailedCallback


class BaseClientError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    @classmethod
    def from_response(
        cls,
        response: httpx.Response,
        comment: Optional[str] = None,
    ) -> "BaseClientError":
        method = response.request.method
        url = response.request.url
        status_code = response.status_code
        content = response.content

        message = (
            f"{method} {url}\n"  # noqa: WPS221 (Strange error on CI)
            f"failed with code {status_code} and payload:\n"
            f"{content!r}"
        )

        if comment is not None:
            message = f"{message}\n\nComment: {comment}"

        return cls(message)

    @classmethod
    def from_callback(
        cls,
        callback: BotAPIMethodFailedCallback,
        comment: Optional[str] = None,
    ) -> "BaseClientError":
        message = (
            f"BotX method call with sync_id `{callback.sync_id!s}` "
            f"failed with: {callback}"
        )

        if comment is not None:
            message = f"{message}\n\nComment: {comment}"

        return cls(message)
