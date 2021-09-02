"""Endpoints for stickers."""
import uuid
from datetime import datetime as dt

from starlette import requests, responses

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
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.content import PNG_DATA


@bind_implementation_to_method(sticker_pack_list.GetStickerPackList)
async def get_sticker_pack_list(request: requests.Request) -> responses.Response:
    """Handle retrieving information of sticker pack list request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with list of sticker packs.
    """
    payload = sticker_pack_list.GetStickerPackList.parse_obj(request.query_params)
    add_request_to_collection(request, payload)

    pagination = stickers.Pagination(after=PNG_DATA)
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
    sticker_pack_list_response = stickers.StickerPackList(
        packs=sticker_packs,
        pagination=pagination,
    )

    return PydanticResponse(
        APIResponse[stickers.StickerPackList](
            result=sticker_pack_list_response,
        ),
    )


@bind_implementation_to_method(sticker_pack.GetStickerPack)
async def get_sticker_pack(request: requests.Request) -> responses.Response:
    """Handle retrieving information of sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information of sticker pack.
    """
    payload = sticker_pack.GetStickerPack.parse_obj(request.path_params)
    add_request_to_collection(request, payload)

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
async def get_sticker_from_sticker_pack(
    request: requests.Request,
) -> responses.Response:
    """Handle retrieving information of sticker from sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with information of sticker from sticker pack.
    """
    payload = sticker.GetSticker.parse_obj(request.path_params)
    add_request_to_collection(request, payload)

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
async def post_add_sticker_into_sticker_pack(
    request: requests.Request,
) -> responses.Response:
    """Handle adding of sticker to sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of adding.
    """
    payload = add_sticker.AddSticker.parse_obj(await request.json())
    add_request_to_collection(request, payload)

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
async def post_create_sticker_pack(request: requests.Request) -> responses.Response:
    """Handle creating of sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of creating.
    """
    payload = create_sticker_pack.CreateStickerPack.parse_obj(request.query_params)
    add_request_to_collection(request, payload)

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
async def post_edit_sticker_pack(request: requests.Request) -> responses.Response:
    """Handle editing of sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of editing.
    """
    payload = edit_sticker_pack.EditStickerPack.parse_obj(await request.json())
    add_request_to_collection(request, payload)

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
    inserted_at = dt.fromisoformat("2019-08-29T11:22:48.358586+00:00")
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
async def post_delete_sticker_pack(request: requests.Request) -> responses.Response:
    """Handle deleting of sticker pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of deleting.
    """
    payload = delete_sticker_pack.DeleteStickerPack.parse_obj(request.path_params)
    add_request_to_collection(request, payload)

    return PydanticResponse(
        APIResponse[str](
            result="sticker_pack_deleted",
        ),
    )


@bind_implementation_to_method(delete_sticker.DeleteSticker)
async def post_delete_sticker_from_sticker_pack(
    request: requests.Request,
) -> responses.Response:
    """Handle deleting of sticker from sticker pack pack request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with result of deleting.
    """
    payload = delete_sticker.DeleteSticker.parse_obj(request.path_params)
    add_request_to_collection(request, payload)

    return PydanticResponse(
        APIResponse[str](
            result="sticker_deleted",
        ),
    )
