"""Definition for "sticker pack was not found" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class StickerPackNotFoundError(BotXAPIError):
    """Error for raising when sticker pack was not found."""

    message_template = "sticker pack {pack_id} not found"

    #: sticker pack ID.
    pack_id: UUID


class StickerPackNotFoundData(BaseModel):
    """Data for error when sticker pack was not found."""

    #: sticker pack ID.
    pack_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "sticker pack getting error" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        StickerPackNotFoundError: raised always.
    """
    parsed_response = APIErrorResponse[StickerPackNotFoundData].parse_obj(
        response.json_body,
    )

    error_data = parsed_response.error_data
    raise StickerPackNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        pack_id=error_data.pack_id,
    )
