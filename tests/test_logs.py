from http import HTTPStatus
from typing import Any, Callable, Dict, Optional, cast
from uuid import UUID

import httpx
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)
from pybotx.models.attachments import AttachmentDocument, OutgoingAttachment

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__attachment__trimmed_in_incoming_message(
    bot_account: BotAccountWithSecret,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    payload = api_incoming_message_factory(
        attachment={
            "data": {
                "content": (
                    "data:text/plain;base64,"
                    "SGVsbG8sIGFtYXppbmcgd29ybGQhIFZlcnkgdmVyeSB2ZXJ5IHZlcnkgdm"
                    "VyeSB2ZXJ5IGxvbmcgdGV4dCB0byB0ZXN0IHRoYXQgdHJpbW1pbmcgY29u"
                    "dGVudCBkb2Vzbid0IGFmZmVjdCBmaWxlIGluIGluY29taW5nIG1lc3NhZ2U="
                ),
                "file_name": "test_file.jpg",
            },
            "type": "image",
        },
    )
    collector = HandlerCollector()
    file_data: Optional[bytes] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal file_data
        file = cast(AttachmentDocument, message.file)
        file_data = file.content

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "...<trimmed>" in loguru_caplog.text
    assert file_data == (
        b"Hello, amazing world! Very very very very very very long text to"
        b" test that trimming content doesn't affect file in incoming message"
    )


async def test__attachment__trimmed_in_outgoing_message(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
            "file": {
                "file_name": "test.txt",
                "data": (
                    "data:text/plain;base64,"
                    "SGVsbG8sIGFtYXppbmcgd29ybGQhIFZlcnkgdmVyeSB2ZXJ5IHZlcnkgdm"
                    "VyeSB2ZXJ5IGxvbmcgdGV4dCB0byB0ZXN0IHRoYXQgdHJpbW1pbmcgY29u"
                    "dGVudCBkb2Vzbid0IGFmZmVjdCBmaWxlIGluIGluY29taW5nIG1lc3NhZ2U="
                ),
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(
            b"Hello, amazing world! Very very very very very very long text to"
            b" test that trimming content doesn't affect file in incoming message",
        )
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(
            async_buffer,
            "test.txt",
        )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.send_message(
            body="Hi!",
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            file=file,
        )

    # - Assert -
    assert "...<trimmed>" in loguru_caplog.text
    assert endpoint.called
