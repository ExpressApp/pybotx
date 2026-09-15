from http import HTTPStatus
from typing import Any
from collections.abc import Callable
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    FastAPIBotAppConfig,
    HandlerCollector,
    IncomingMessage,
    SmartAppEvent,
    create_fastapi_bot_app,
)
from pybotx.models.sync_smartapp_event import (
    BotAPISyncSmartAppEventErrorResponse,
    BotAPISyncSmartAppEventResultResponse,
)

# - Bot setup -
collector = HandlerCollector()


@collector.command("/debug", description="Simple debug command")
async def debug_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Hi!")


@collector.sync_smartapp_event
async def handle_sync_smartapp_event(
    event: SmartAppEvent,
    _: Bot,
) -> BotAPISyncSmartAppEventResultResponse:
    return BotAPISyncSmartAppEventResultResponse.from_domain(
        data=event.data["params"],
        files=event.files,
    )


def bot_factory(
    bot_accounts: list[BotAccountWithSecret],
    bot_collector: HandlerCollector | None = None,
) -> Bot:
    return Bot(collectors=[bot_collector or collector], bot_accounts=bot_accounts)


def fastapi_factory(bot: Bot, *, verify_request: bool = False) -> FastAPI:
    return create_fastapi_bot_app(
        bot=bot,
        config=FastAPIBotAppConfig(
            verify_request=verify_request,
            verify_callback_request=False,
            smartapp_request_path="/smartapps/request",
            healthcheck_prefix=None,
        ),
    )


# https://www.uvicorn.org/#application-factories
def asgi_factory() -> FastAPI:
    bot_accounts = [
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ]
    bot = bot_factory(bot_accounts=bot_accounts)
    return fastapi_factory(bot)


# - Tests -
@pytest.fixture
def bot(bot_account: BotAccountWithSecret) -> Bot:
    return bot_factory(bot_accounts=[bot_account])


pytestmark = [
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


def test__web_app__bot_status(
    bot_id: UUID,
    bot: Bot,
) -> None:
    # - Arrange -
    query_params = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "result": {
            "commands": [
                {
                    "body": "/debug",
                    "description": "Simple debug command",
                    "name": "/debug",
                },
            ],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }


def test__web_app__bot_command(
    respx_mock: MockRouter,
    bot_id: UUID,
    host: str,
    bot: Bot,
) -> None:
    # - Arrange -
    direct_notification_endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    command_payload: dict[str, Any] = {
        "bot_id": str(bot_id),
        "command": {
            "body": "/debug",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
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
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }

    callback_payload = {
        "status": "ok",
        "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
        "result": {},
    }

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        command_response = test_client.post(
            "/command",
            json=command_payload,
        )

        callback_response = test_client.post(
            "/notification/callback",
            json=callback_payload,
        )

    # - Assert -
    assert command_response.status_code == HTTPStatus.ACCEPTED
    assert direct_notification_endpoint.called
    assert callback_response.status_code == HTTPStatus.ACCEPTED


def test__web_app__unknown_bot_response(
    bot: Bot,
) -> None:
    # - Arrange -
    payload: dict[str, Any] = {
        "bot_id": "c755e147-30a5-45df-b46a-c75aa6089c8f",
        "command": {
            "body": "/debug",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
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
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        response = test_client.post(
            "/command",
            json=payload,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE


def test__web_app__disabled_bot_response(
    bot: Bot,
) -> None:
    # - Arrange -
    payload = {"incorrect": "request"}

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        response = test_client.post(
            "/command",
            json=payload,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {
        "error_data": {"status_message": "Bot command validation error"},
        "errors": [],
        "reason": "bot_disabled",
    }


def test__web_app__unverified_request_response(
    bot: Bot,
) -> None:
    # - Act -
    with TestClient(fastapi_factory(bot, verify_request=True)) as test_client:
        response = test_client.get(
            "/status",
            params={},
        )

    # - Assert -
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "error_data": {"status_message": "The authorization token was not provided."},
        "errors": [],
        "reason": "unverified_request",
    }


def test__web_app__sync_smartapp_event__success(bot: Bot, bot_id: UUID) -> None:
    # - Arrange -
    request_payload = {
        "bot_id": str(bot_id),
        "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
        "sender_info": {
            "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
            "platform": "web",
            "udid": "49eac56a-c0d8-51d7-863e-925028f05110",
        },
        "method": "list.get",
        "payload": {
            "data": {"category_id": 1},
            "files": [
                {
                    "file": "/uploads/files/b0232da0bf3d406eb5653e37b2bb6517.bin",
                    "file_name": "cts1-test.ast-innovation.ru.har",
                    "file_size": 349372,
                    "file_hash": "qVSzEUJITWP+TgCvcF3UCzQrBaY3RHqB92CHObz4E70=",
                    "file_mime_type": "application/octet-stream",
                    "chunk_size": 2097152,
                    "file_encryption_algo": "stream",
                    "file_id": "a0ec914f-8235-5021-9b8d-05c3cd303536",
                    "type": "document",
                },
            ],
        },
    }

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        response = test_client.post(
            "/smartapps/request",
            json=request_payload,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "status": "ok",
        "result": {
            "data": {"category_id": 1},
            "files": [
                {
                    "file": "/uploads/files/b0232da0bf3d406eb5653e37b2bb6517.bin",
                    "file_name": "cts1-test.ast-innovation.ru.har",
                    "file_size": 349372,
                    "file_hash": "qVSzEUJITWP+TgCvcF3UCzQrBaY3RHqB92CHObz4E70=",
                    "file_mime_type": "application/octet-stream",
                    "chunk_size": 2097152,
                    "file_encryption_algo": "stream",
                    "file_id": "a0ec914f-8235-5021-9b8d-05c3cd303536",
                    "type": "document",
                },
            ],
        },
    }


def test__web_app__sync_smartapp_event__error(
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    api_sync_smartapp_event_factory: Callable[..., dict[str, Any]],
) -> None:
    # - Arrange -
    request_payload = api_sync_smartapp_event_factory(bot_id=bot_id)
    local_collector = HandlerCollector()

    @local_collector.sync_smartapp_event
    async def handle_sync_smartapp_event_with_error(
        *_: Any,
    ) -> BotAPISyncSmartAppEventErrorResponse:
        return BotAPISyncSmartAppEventErrorResponse.from_domain(
            errors=[{"id": "Error", "reason": "some error"}],
        )

    bot = bot_factory(bot_accounts=[bot_account], bot_collector=local_collector)

    # - Act -
    with TestClient(fastapi_factory(bot)) as test_client:
        response = test_client.post(
            "/smartapps/request",
            json=request_payload,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "status": "error",
        "reason": "smartapp_error",
        "errors": [{"id": "Error", "reason": "some error"}],
        "error_data": {},
    }
