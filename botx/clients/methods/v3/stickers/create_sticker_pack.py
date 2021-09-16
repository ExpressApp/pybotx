"""Method for creating new sticker pack."""
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.http import HTTPRequest
from botx.models.stickers import StickerPack


class CreateStickerPack(AuthorizedBotXMethod[StickerPack]):
    """Method for creating sticker pack."""

    __url__ = "/api/v3/botx/stickers/packs"
    __method__ = "POST"
    __returning__ = StickerPack

    #: sticker pack name.
    name: str

    #: author HUID.
    user_huid: UUID

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
