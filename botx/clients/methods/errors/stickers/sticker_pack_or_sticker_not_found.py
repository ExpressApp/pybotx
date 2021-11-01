"""Definition for "sticker pack or sticker was not found" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class StickerPackOrStickerNotFoundError(BotXAPIError):
    """Error for raising when sticker pack or sticker was not found."""

    message_template = "sticker pack {pack_id} or sticker {sticker_id} was not found"

    #: sticker pack ID.
    pack_id: UUID

    #: sticker ID.
    sticker_id: UUID


class StickerPackOrStickerNotFoundData(BaseModel):
    """Data for error when sticker pack or sticker was not found."""

    #: sticker pack ID.
    pack_id: UUID

    #: sticker ID.
    sticker_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "sticker getting error" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        StickerPackOrStickerNotFoundError: raised always.
    """
    parsed_response = APIErrorResponse[StickerPackOrStickerNotFoundData].parse_obj(
        response.json_body,
    )

    error_data = parsed_response.error_data
    raise StickerPackOrStickerNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        pack_id=error_data.pack_id,
        sticker_id=error_data.sticker_id,
    )
