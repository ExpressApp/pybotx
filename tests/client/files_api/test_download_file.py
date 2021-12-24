from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatNotFoundError,
    FileDeletedError,
    FileMetadataNotFound,
    HandlerCollector,
    InvalidBotXStatusCodeError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__unexpected_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "anything_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": "84a12e71-3efc-5c34-87d5-84e3d9ad64fd",
                    "error_description": "42",
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXStatusCodeError) as exc:
            await bot.download_file(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                file_id=UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80"),
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "anything_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__file_metadata_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "file_metadata_not_found",
                "errors": [],
                "error_data": {
                    "file_id": "e48c5612-b94f-4264-adc2-1bc36445a226",
                    "group_chat_id": "84a12e71-3efc-5c34-87d5-84e3d9ad64fd",
                    "error_description": "File with specified file_id and group_chat_id not found in file service",
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(FileMetadataNotFound) as exc:
            await bot.download_file(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                file_id=UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80"),
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "file_metadata_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__file_deleted_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NO_CONTENT,
            json={
                "status": "error",
                "reason": "file_deleted",
                "errors": [],
                "error_data": {
                    "link": "/example/file.jpeg",
                    "error_description": "File at the specified link has been deleted",
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(FileDeletedError) as exc:
            await bot.download_file(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                file_id=UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80"),
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "file_deleted" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__chat_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": "84a12e71-3efc-5c34-87d5-84e3d9ad64fd",
                    "error_description": "Chat with id 84a12e71-3efc-5c34-87d5-84e3d9ad64fd not found",
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.download_file(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                file_id=UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80"),
                async_buffer=async_buffer,
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content=b"Hello, world!\n",
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.download_file(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            file_id=UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80"),
            async_buffer=async_buffer,
        )

    # - Assert -
    assert await async_buffer.read() == b"Hello, world!\n"
    assert endpoint.called
