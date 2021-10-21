import logging
from http import HTTPStatus
from typing import AsyncGenerator, Generator
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile
from loguru import logger

from botx import Bot, BotAccount, HandlerCollector
from botx.bot.contextvars import bot_id_var, bot_var, chat_id_var


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
def set_contexvars(
    httpx_client: httpx.AsyncClient,
    bot_account: BotAccount,
    bot_id: UUID,
    chat_id: UUID,
) -> None:
    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    bot_var.set(built_bot)
    bot_id_var.set(bot_id)
    chat_id_var.set(chat_id)


@pytest.fixture
async def async_buffer() -> AsyncGenerator[NamedTemporaryFile, None]:
    async with NamedTemporaryFile("wb+") as async_buffer:
        yield async_buffer
