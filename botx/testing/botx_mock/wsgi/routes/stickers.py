"""Endpoints for stickers."""
import uuid
from datetime import datetime as dt

from molten import Request, RequestData, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.stickers import (
    add_sticker,
    create_sticker_pack,
    delete_sticker,
    delete_sticker_pack,
    edit_sticker_pack,
    sticker,
    sticker_pack,
    sticker_pack_list,
)
from botx.models import stickers
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(sticker_pack_list.GetStickerPackList)
def get_sticker_pack_list(request: Request, settings: Settings) -> Response:
    """Handle retrieving information of sticker pack list request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with list of sticker packs.
    """
    payload = sticker_pack_list.GetStickerPackList.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    pagination = stickers.Pagination(
        after="ABAmCAFTpX1ajK8O_ezuPEQ1AA0ACnVwZGF0ZWRfYXQAf____gAAAAA=",
    )
    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    sticker_packs = [
        stickers.StickerPackPreview(
            id=uuid.uuid4(),
            name="Test sticker pack",
            public=False,
            stickers_count=1,
            inserted_at=inserted_at,
        ),
    ]
    pack_list = stickers.StickerPackList(
        packs=sticker_packs,
        pagination=pagination,
    )

    return PydanticResponse(
        APIResponse[stickers.StickerPackList](
            result=pack_list,
        ),
    )


@bind_implementation_to_method(sticker_pack.GetStickerPack)
def get_sticker_pack(request: Request, settings: Settings) -> Response:
    """Handle retrieving information of sticker pack request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information of sticker pack.
    """
    payload = sticker_pack.GetStickerPack.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    pack_stickers = [
        stickers.Sticker(
            id=uuid.uuid4(),
            emoji="🐢",
            link="http://some_link.com",
            inserted_at=inserted_at,
            updated_at=inserted_at,
        ),
    ]
    sticker_pack_preview = stickers.StickerPack(
        id=uuid.uuid4(),
        name="Test sticker pack",
        preview=None,
        public=False,
        stickers_order=None,
        stickers=pack_stickers,
        inserted_at=inserted_at,
        updated_at=inserted_at,
        deleted_at=None,
    )

    return PydanticResponse(
        APIResponse[stickers.StickerPack](
            result=sticker_pack_preview,
        ),
    )


@bind_implementation_to_method(sticker.GetSticker)
def get_sticker_from_sticker_pack(request: Request, settings: Settings) -> Response:
    """Handle retrieving information of sticker from sticker pack request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with information of sticker from sticker pack.
    """
    payload = sticker.GetSticker.parse_obj(request.params)

    add_request_to_collection(settings, payload)
    sticker_from_sticker_pack = stickers.StickerFromPack(
        id=uuid.uuid4(),
        emoji="🐢",
        link="http://some_link.com",
        preview="http://preview_link.com",
    )

    return PydanticResponse(
        APIResponse[stickers.StickerFromPack](
            result=sticker_from_sticker_pack,
        ),
    )


@bind_implementation_to_method(add_sticker.AddSticker)
def post_add_sticker_into_sticker_pack(
    request_data: RequestData,
    settings: Settings,
) -> Response:
    """Handle adding of sticker to sticker pack request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of adding.
    """
    payload = add_sticker.AddSticker.parse_obj(request_data)
    add_request_to_collection(settings, payload)

    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    sticker_from_sticker_pack = stickers.Sticker(
        id=uuid.uuid4(),
        emoji="🐢",
        link="http://some_link.com",
        inserted_at=inserted_at,
        updated_at=inserted_at,
    )

    return PydanticResponse(
        APIResponse[stickers.Sticker](
            result=sticker_from_sticker_pack,
        ),
    )


@bind_implementation_to_method(create_sticker_pack.CreateStickerPack)
def post_create_sticker_pack(request: Request, settings: Settings) -> Response:
    """Handle creating of sticker pack request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with result of creating.
    """
    payload = create_sticker_pack.CreateStickerPack.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    pack_stickers = [
        stickers.Sticker(
            id=uuid.uuid4(),
            emoji="🐢",
            link="http://some_link.com",
            inserted_at=inserted_at,
            updated_at=inserted_at,
        ),
    ]
    sticker_from_sticker_pack = stickers.StickerPack(
        id=uuid.uuid4(),
        name="Test sticker pack",
        preview=None,
        public=False,
        stickers_order=None,
        stickers=pack_stickers,
        inserted_at=inserted_at,
        updated_at=inserted_at,
        deleted_at=None,
    )

    return PydanticResponse(
        APIResponse[stickers.StickerPack](
            result=sticker_from_sticker_pack,
        ),
    )


@bind_implementation_to_method(edit_sticker_pack.EditStickerPack)
def post_edit_sticker_pack(request_data: RequestData, settings: Settings) -> Response:
    """Handle editing of sticker pack request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with result of editing.
    """
    payload = edit_sticker_pack.EditStickerPack.parse_obj(request_data)
    add_request_to_collection(settings, payload)

    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
    pack_stickers = [
        stickers.Sticker(
            id=uuid.uuid4(),
            emoji="🐢",
            link="http://some_link.com",
            inserted_at=inserted_at,
            updated_at=inserted_at,
        ),
    ]
    sticker_from_sticker_pack = stickers.StickerPack(
        id=uuid.uuid4(),
        name="Test sticker pack",
        preview=None,
        public=False,
        stickers_order=None,
        stickers=pack_stickers,
        inserted_at=inserted_at,
        updated_at=inserted_at,
        deleted_at=None,
    )

    return PydanticResponse(
        APIResponse[stickers.StickerPack](
            result=sticker_from_sticker_pack,
        ),
    )


@bind_implementation_to_method(delete_sticker_pack.DeleteStickerPack)
def post_delete_sticker_pack(request: Request, settings: Settings) -> Response:
    """Handle deleting of sticker pack request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with result of deleting.
    """
    payload = delete_sticker_pack.DeleteStickerPack.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    return PydanticResponse(
        APIResponse[str](
            result="sticker_pack_deleted",
        ),
    )


@bind_implementation_to_method(delete_sticker.DeleteSticker)
def delete_sticker_from_sticker_pack(request: Request, settings: Settings) -> Response:
    """Handle deleting of sticker from sticker pack request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with result of deleting.
    """
    payload = delete_sticker.DeleteSticker.parse_obj(request.params)
    add_request_to_collection(settings, payload)

    return PydanticResponse(
        APIResponse[str](
            result="sticker_deleted",
        ),
    )
