"""Method for editing sticker pack."""
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import urljoin
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors.stickers import sticker_pack_not_found
from botx.clients.types.http import HTTPRequest
from botx.models.stickers import StickerPack


class EditStickerPack(AuthorizedBotXMethod[StickerPack]):
    """Method for editing sticker pack."""

    __url__ = "/api/v3/botx/stickers/packs/{pack_id}"
    __method__ = "PUT"
    __returning__ = StickerPack
    __errors_handlers__ = {
        HTTPStatus.NOT_FOUND: (sticker_pack_not_found.handle_error,),
    }

    # : sticker pack ID.
    pack_id: UUID

    # : sticker pack name.
    name: str

    #: sticker pack preview.
    preview: Optional[UUID]

    #: stickers order in sticker pack.
    stickers_order: Optional[List[UUID]]

    @property
    def url(self) -> str:
        """Full URL for request with filling pack_id."""
        api_url = self.__url__.format(pack_id=self.pack_id)
        return urljoin(super().url, api_url)

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
            query_params={},
            json_body=request_params,
            expected_type=self.expected_type,
        )
