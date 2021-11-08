import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any, AsyncGenerator, Callable, Dict, Generator, Optional
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile
from loguru import logger
from pydantic import BaseModel

from botx import BotAccount


@pytest.fixture
def datetime_formatter() -> Callable[[str], datetime]:
    class DateTimeFormatter(BaseModel):  # noqa: WPS431
        value: datetime

    def factory(dt_str: str) -> datetime:
        return DateTimeFormatter(value=dt_str).value

    return factory


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def chat_id() -> UUID:
    return UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa")


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def file_id() -> UUID:
    return UUID("c3b9def2-b2c8-4732-b61f-99b9b110fa80")


@pytest.fixture
def bot_account(host: str, bot_id: UUID) -> BotAccount:
    return BotAccount(
        host=host,
        bot_id=bot_id,
        secret_key="bee001",
    )


@pytest.fixture
def mock_authorization(
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    respx.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )


@pytest.fixture
def bot_signature() -> str:
    return "E050AEEA197E0EF0A6E1653E18B7D41C7FDEC0FCFBA44C44FCCD2A88CEABD130"


@pytest.fixture()
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    class PropogateHandler(logging.Handler):  # noqa: WPS431
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def sync_id() -> UUID:
    return UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")


async def log_request(request: httpx.Request) -> None:
    if isinstance(
        request.stream,  # type: ignore
        httpx._multipart.MultipartStream,  # noqa: WPS437
    ):
        content = b"<stream>"
    else:
        content = request.content

    logger.debug(
        "\n"
        f"Endpoint: {request.method} {request.url}\n"
        f"Headers: {request.headers}\n"
        f"Payload: {content!r}",
    )


async def log_response(response: httpx.Response) -> None:
    logger.debug(
        f"\nHeaders: {response.headers}\nStatus code: {response.status_code}\n",
    )


@pytest.fixture
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        event_hooks={"request": [log_request], "response": [log_response]},
    ) as client:
        yield client


@pytest.fixture
async def async_buffer() -> AsyncGenerator[NamedTemporaryFile, None]:
    async with NamedTemporaryFile("wb+") as async_buffer:
        yield async_buffer


@pytest.fixture
def incoming_message_payload_factory() -> Callable[..., Dict[str, Any]]:
    def decorator(
        *,
        bot_id: Optional[UUID] = None,
        group_chat_id: Optional[UUID] = None,
        user_huid: Optional[UUID] = None,
        host: Optional[str] = None,
        attachment: Optional[Dict[str, Any]] = None,
        async_file: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "bot_id": str(bot_id) if bot_id else "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
            "command": {
                "body": "/hello",
                "command_type": "user",
                "data": {},
                "metadata": {},
            },
            "attachments": [attachment] if attachment else [],
            "async_files": [async_file] if async_file else [],
            "source_sync_id": None,
            "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
            "from": {
                "ad_domain": None,
                "ad_login": None,
                "app_version": None,
                "chat_type": "chat",
                "device": None,
                "device_meta": {
                    "permissions": None,
                    "pushes": False,
                    "timezone": "Europe/Moscow",
                },
                "device_software": None,
                "group_chat_id": (
                    str(group_chat_id)
                    if group_chat_id
                    else "30dc1980-643a-00ad-37fc-7cc10d74e935"
                ),
                "host": host or "cts.example.com",
                "is_admin": True,
                "is_creator": True,
                "locale": "en",
                "manufacturer": None,
                "platform": None,
                "platform_package_id": None,
                "user_huid": (
                    str(user_huid)
                    if user_huid
                    else "f16cdc5f-6366-5552-9ecd-c36290ab3d11"
                ),
                "username": None,
            },
            "proto_version": 4,
            "entities": [],
        }

    return decorator
