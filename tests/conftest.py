import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional
from unittest.mock import Mock
from uuid import UUID, uuid4

import httpx
import jwt
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from pydantic import BaseModel
from respx.router import MockRouter

from pybotx import (
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
)
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.logger import logger


@pytest.fixture(autouse=True)
def enable_logger() -> None:
    logger.enable("pybotx")


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage([bot_account])
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage


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
def cts_url() -> str:
    return "https://cts.example.com"


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def bot_account(cts_url: str, bot_id: UUID) -> BotAccountWithSecret:
    return BotAccountWithSecret(
        id=bot_id,
        cts_url=cts_url,
        secret_key="bee001",
    )


@pytest.fixture
def authorization_token_payload(bot_account: BotAccountWithSecret) -> Dict[str, Any]:
    return {
        "aud": [str(bot_account.id)],
        "exp": datetime(year=3000, month=1, day=1).timestamp(),
        "iat": datetime(year=2000, month=1, day=1).timestamp(),
        "iss": bot_account.host,
        "jti": "2uqpju31h6dgv4f41c005e1i",
        "nbf": datetime(year=2000, month=1, day=1).timestamp(),
    }


@pytest.fixture
def authorization_header(
    bot_account: BotAccountWithSecret,
    authorization_token_payload: Dict[str, Any],
) -> Dict[str, str]:
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )
    return {"authorization": f"Bearer {token}"}


@pytest.fixture
def bot_signature() -> str:
    return "E050AEEA197E0EF0A6E1653E18B7D41C7FDEC0FCFBA44C44FCCD2A88CEABD130"


@pytest.fixture
def mock_authorization(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    """Fixture should be used as a marker."""
    respx_mock.get(
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


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: List[pytest.Function]) -> None:
    for item in items:
        if item.get_closest_marker("mock_authorization"):
            item.fixturenames.append("mock_authorization")


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
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
async def async_buffer() -> AsyncGenerator[NamedTemporaryFile, None]:
    async with NamedTemporaryFile("wb+") as async_buffer:
        yield async_buffer


@pytest.fixture
def api_incoming_message_factory() -> Callable[..., Dict[str, Any]]:
    def decorator(
        *,
        body: str = "/hello",
        bot_id: Optional[UUID] = None,
        group_chat_id: Optional[UUID] = None,
        user_huid: Optional[UUID] = None,
        host: Optional[str] = None,
        attachment: Optional[Dict[str, Any]] = None,
        async_file: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "bot_id": str(bot_id) if bot_id else "24348246-6791-4ac0-9d86-b948cd6a0e46",
            "command": {
                "body": body,
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
                "user_udid": None,
                "username": None,
            },
            "proto_version": 4,
            "entities": [],
        }

    return decorator


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
) -> Callable[..., IncomingMessage]:
    def decorator(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot=BotAccount(
                id=bot_id,
                host="cts.example.com",
            ),
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserSender(
                huid=uuid4(),
                udid=None,
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                device=UserDevice(
                    manufacturer=None,
                    device_name=None,
                    os=None,
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    app_version=None,
                    locale=None,
                ),
            ),
            chat=Chat(
                id=uuid4(),
                type=ChatTypes.PERSONAL_CHAT,
            ),
            raw_command=None,
        )

    return decorator


@pytest.fixture
def correct_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture
def incorrect_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture(autouse=True)
def prevent_http_requests(respx_mock: MockRouter) -> None:
    pass
