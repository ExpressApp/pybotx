from http import HTTPStatus
from typing import List
from uuid import UUID

import httpx
import pytest
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from loguru import logger
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    UnknownBotAccountError,
    build_bot_disabled_response,
    build_command_accepted_response,
)

# - Bot setup -
collector = HandlerCollector()


@collector.command("/debug", description="Simple debug command")
async def debug_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Hi!")


def bot_factory(
    bot_accounts: List[BotAccountWithSecret],
) -> Bot:
    return Bot(collectors=[collector], bot_accounts=bot_accounts)


# - FastAPI integration -
def get_bot(request: Request) -> Bot:
    assert isinstance(request.app.state.bot, Bot)

    return request.app.state.bot


bot_dependency = Depends(get_bot)

router = APIRouter()


@router.post("/command")
async def command_handler(
    request: Request,
    bot: Bot = bot_dependency,
) -> JSONResponse:
    try:
        bot.async_execute_raw_bot_command(await request.json())
    except ValueError:
        error_label = "Bot command validation error"
        logger.exception(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    except UnknownBotAccountError as exc:
        error_label = f"No credentials for bot {exc.bot_id}"
        logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


@router.get("/status")
async def status_handler(request: Request, bot: Bot = bot_dependency) -> JSONResponse:
    status = await bot.raw_get_status(dict(request.query_params))
    return JSONResponse(status)


@router.post("/notification/callback")
async def callback_handler(
    request: Request,
    bot: Bot = bot_dependency,
) -> JSONResponse:
    await bot.set_raw_botx_method_result(await request.json())
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


def fastapi_factory(bot: Bot) -> FastAPI:
    application = FastAPI()
    application.state.bot = bot

    application.add_event_handler("startup", bot.startup)
    application.add_event_handler("shutdown", bot.shutdown)

    application.include_router(router)

    return application


# https://www.uvicorn.org/#application-factories
def asgi_factory() -> FastAPI:
    bot_accounts = [
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
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

    command_payload = {
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
    payload = {
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
