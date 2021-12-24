from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper
from botx.models.async_files import Document, Image, Video, Voice
from botx.models.enums import AttachmentTypes


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_smartapp_event__miminally_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/smartapps/event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "ref": "921763b3-77e8-4f37-b97e-20f4517949b8",
            "smartapp_id": str(bot_id),
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "data": {"key": "value"},
            "opts": {},
            "smartapp_api_version": 1,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "smartapp_event_pushed",
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
        await bot.send_smartapp_event(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            data={"key": "value"},
            ref=UUID("921763b3-77e8-4f37-b97e-20f4517949b8"),
        )

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_smartapp_event__maximum_filled_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/smartapps/event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "ref": "921763b3-77e8-4f37-b97e-20f4517949b8",
            "smartapp_id": str(bot_id),
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "data": {"key": "value"},
            "opts": {"option": True},
            "smartapp_api_version": 1,
            "async_files": [
                {
                    "type": "image",
                    "file": "https://link.to/file",
                    "file_mime_type": "image/png",
                    "file_name": "pass.png",
                    "file_size": 1502345,
                    "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                    "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                },
                {
                    "type": "video",
                    "file": "https://link.to/file",
                    "file_mime_type": "video/mp4",
                    "file_name": "pass.mp4",
                    "file_size": 1502345,
                    "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                    "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                    "duration": 10,
                },
                {
                    "type": "document",
                    "file": "https://link.to/file",
                    "file_mime_type": "plain/text",
                    "file_name": "pass.txt",
                    "file_size": 1502345,
                    "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                    "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                },
                {
                    "type": "voice",
                    "file": "https://link.to/file",
                    "file_mime_type": "audio/mp3",
                    "file_name": "pass.mp3",
                    "file_size": 1502345,
                    "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                    "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                    "duration": 10,
                },
            ],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "smartapp_event_pushed",
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
        await bot.send_smartapp_event(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            ref=UUID("921763b3-77e8-4f37-b97e-20f4517949b8"),
            data={"key": "value"},
            opts={"option": True},
            files=[
                Image(
                    type=AttachmentTypes.IMAGE,
                    filename="pass.png",
                    size=1502345,
                    is_async_file=True,
                    _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
                    _file_url="https://link.to/file",
                    _file_mimetype="image/png",
                    _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                ),
                Video(
                    type=AttachmentTypes.VIDEO,
                    filename="pass.mp4",
                    size=1502345,
                    is_async_file=True,
                    duration=10,
                    _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
                    _file_url="https://link.to/file",
                    _file_mimetype="video/mp4",
                    _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                ),
                Document(
                    type=AttachmentTypes.DOCUMENT,
                    filename="pass.txt",
                    size=1502345,
                    is_async_file=True,
                    _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
                    _file_url="https://link.to/file",
                    _file_mimetype="plain/text",
                    _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                ),
                Voice(
                    type=AttachmentTypes.VOICE,
                    filename="pass.mp3",
                    size=1502345,
                    is_async_file=True,
                    duration=10,
                    _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
                    _file_url="https://link.to/file",
                    _file_mimetype="audio/mp3",
                    _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                ),
            ],
        )

    # - Assert -
    assert endpoint.called
