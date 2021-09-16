"""Method for adding stickers into sticker pack."""
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors.stickers import image_not_valid, sticker_pack_not_found
from botx.clients.types.http import HTTPRequest
from botx.models.stickers import Sticker


class AddSticker(AuthorizedBotXMethod[Sticker]):
    """Method for adding stickers into sticker pack."""

    __url__ = "/api/v3/botx/stickers/packs/{pack_id}/stickers/"
    __method__ = "POST"
    __returning__ = Sticker
    __errors_handlers__ = {
        HTTPStatus.BAD_REQUEST: (
            sticker_pack_not_found.handle_error,
            image_not_valid.handle_error,
        ),
    }

    #: sticker pack ID.
    pack_id: UUID

    #: emoji that the sticker will be associated with.
    emoji: str

    #: sticker image.
    image: str

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
            json_body=dict(request_params),  # type: ignore
            expected_type=self.expected_type,
        )
