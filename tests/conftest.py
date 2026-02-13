import logging
import socket
from datetime import datetime
from http import HTTPStatus
from typing import Any
from contextlib import AbstractAsyncContextManager
from collections.abc import AsyncGenerator, Callable, Generator
from unittest.mock import Mock
from uuid import UUID, uuid4

import httpx
import jwt
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    HandlerCollector,
    IncomingMessage,
    SmartAppEvent,
    UserDevice,
    UserSender,
    BotXAuthVersion,
    lifespan_wrapper,
)
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.logger import logger
from pybotx.models.sync_smartapp_event import BotAPISyncSmartAppEventResultResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from tests.fixtures.users_api import (  # noqa: F401
    user_from_search_with_data,
    user_from_search_with_data_json,
    user_from_search_without_data,
    user_from_search_without_data_json,
)


@pytest.fixture(autouse=True)
def enable_logger() -> None:
    logger.enable("pybotx")


@pytest.fixture(autouse=True)
def block_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("allow_network"):
        return

    def guard(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError(
            "Network access is disabled during tests. "
            "Use @pytest.mark.allow_network to override.",
        )

    monkeypatch.setattr(socket, "create_connection", guard)
    monkeypatch.setattr(socket.socket, "connect", guard, raising=True)


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage(
        [bot_account],
        auth_version=BotXAuthVersion.V1,
    )
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage


@pytest.fixture
def datetime_formatter() -> Callable[[str], datetime]:
    class DateTimeFormatter(BaseModel):
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
def call_id() -> UUID:
    return uuid4()


@pytest.fixture
def bot_account(cts_url: str, bot_id: UUID) -> BotAccountWithSecret:
    return BotAccountWithSecret(
        id=bot_id,
        cts_url=cts_url,
        secret_key="bee001bee001bee001bee001bee001bee001",
    )


@pytest.fixture
def authorization_token_payload(bot_account: BotAccountWithSecret) -> dict[str, Any]:
    return {
        "aud": bot_account.host,
        "exp": datetime(year=3000, month=1, day=1).timestamp(),
        "iat": datetime(year=2000, month=1, day=1).timestamp(),
        "iss": str(bot_account.id),
        "jti": "2uqpju31h6dgv4f41c005e1i",
        "nbf": datetime(year=2000, month=1, day=1).timestamp(),
        "version": 2,
    }


@pytest.fixture
def authorization_token_payload_v1(bot_account: BotAccountWithSecret) -> dict[str, Any]:
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
    authorization_token_payload: dict[str, Any],
) -> dict[str, str]:
    token = jwt.encode(
        payload=authorization_token_payload,
        key=bot_account.secret_key,
    )
    return {"authorization": f"Bearer {token}"}


@pytest.fixture
def authorization_header_v1(
    bot_account: BotAccountWithSecret,
    authorization_token_payload_v1: dict[str, Any],
) -> dict[str, str]:
    token = jwt.encode(
        payload=authorization_token_payload_v1,
        key=bot_account.secret_key,
    )
    return {"authorization": f"Bearer {token}"}


@pytest.fixture
def bot_signature() -> str:
    return "5393FDE463800BB05C4271111AF68D54A4B5EC03EBE808BC2B1FCB4F91BE2DCF"


@pytest.fixture
def mock_authorization(
    respx_mock: MockRouter,
    monkeypatch: pytest.MonkeyPatch,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    """Fixture should be used as a marker."""
    monkeypatch.setattr(
        BotAccountsStorage,
        "build_jwt_v2",
        lambda _self, _bot_id: "token",
    )
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


@pytest.fixture
def bot_factory(
    bot_account: BotAccountWithSecret,
) -> Callable[..., AbstractAsyncContextManager[Bot]]:
    @asynccontextmanager
    async def factory(
        *,
        collectors: list[HandlerCollector] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Bot, None]:
        collectors = collectors or [HandlerCollector()]
        bot = Bot(collectors=collectors, bot_accounts=[bot_account], **kwargs)
        async with lifespan_wrapper(bot) as running_bot:
            yield running_bot

    return factory


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    for item in items:
        if item.get_closest_marker("mock_authorization"):
            item.fixturenames.append("mock_authorization")


@pytest.fixture()
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    class PropogateHandler(logging.Handler):
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
def api_incoming_message_factory() -> Callable[..., dict[str, Any]]:
    def decorator(
        *,
        body: str = "/hello",
        command_type: str = "user",
        data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        bot_id: UUID | None = None,
        group_chat_id: UUID | None = None,
        user_huid: UUID | None = None,
        host: str | None = None,
        attachment: dict[str, Any] | None = None,
        async_file: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "bot_id": str(bot_id) if bot_id else "24348246-6791-4ac0-9d86-b948cd6a0e46",
            "command": {
                "body": body,
                "command_type": command_type,
                "data": data if data else {},
                "metadata": metadata if metadata else {},
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
def api_sync_smartapp_event_factory() -> Callable[..., dict[str, Any]]:
    def decorator(
        *,
        bot_id: UUID | None = None,
        group_chat_id: UUID | None = None,
        user_huid: UUID | None = None,
        async_file: dict[str, Any] | None = None,
        method: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "bot_id": str(bot_id) if bot_id else "8dada2c8-67a6-4434-9dec-570d244e78ee",
            "group_chat_id": (
                str(group_chat_id)
                if group_chat_id
                else "30dc1980-643a-00ad-37fc-7cc10d74e935"
            ),
            "sender_info": {
                "user_huid": (
                    str(user_huid)
                    if user_huid
                    else "f16cdc5f-6366-5552-9ecd-c36290ab3d11"
                ),
                "platform": "web",
                "udid": "49eac56a-c0d8-51d7-863e-925028f05110",
            },
            "method": method or "list.get",
            "payload": {
                "ref": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "data": params or {},
                "files": [async_file] if async_file else [],
            },
        }

    return decorator


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
) -> Callable[..., IncomingMessage]:
    def decorator(
        *,
        body: str = "",
        ad_login: str | None = None,
        ad_domain: str | None = None,
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


@pytest.fixture
def collector_with_sync_smartapp_event_handler() -> HandlerCollector:
    collector = HandlerCollector()

    @collector.sync_smartapp_event
    async def handle_sync_smartapp_event(
        event: SmartAppEvent,
        _: Bot,
    ) -> BotAPISyncSmartAppEventResultResponse:
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data=event.data,
            files=event.files,
        )

    return collector


@pytest.fixture
def smartapp_event(bot_id: UUID, host: str) -> SmartAppEvent:
    return SmartAppEvent(
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        raw_command=None,
        ref=uuid4(),
        smartapp_id=bot_id,
        data={},
        opts={},
        smartapp_api_version=1,
        files=[],
        chat=Chat(
            id=uuid4(),
            type=ChatTypes.PERSONAL_CHAT,
        ),
        sender=UserSender(
            huid=uuid4(),
            udid=None,
            ad_login=None,
            ad_domain=None,
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
    )
