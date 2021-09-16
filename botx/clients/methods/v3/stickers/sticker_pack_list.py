"""Method for getting sticker pack list."""
from typing import Optional
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.http import HTTPRequest
from botx.models.stickers import StickerPackList


class GetStickerPackList(AuthorizedBotXMethod[StickerPackList]):
    """Method for getting sticker pack list."""

    __url__ = "/api/v3/botx/stickers/packs"
    __method__ = "GET"
    __returning__ = StickerPackList

    #: author HUID.
    user_huid: Optional[UUID]

    #: returning value count.
    limit: int

    #: cursor hash for pagination.
    after: Optional[str] = None

    def build_http_request(self) -> HTTPRequest:
        """Build HTTP request that can be used by clients for making real requests.

        Returns:
            Built HTTP request.
        """
        request_params = self.build_serialized_dict()

        return HTTPRequest.construct(
            method=self.http_method,
            url=self.url,
            headers=self.headers,
            query_params=dict(request_params),  # type: ignore
            json_body={},
            expected_type=self.expected_type,
        )
