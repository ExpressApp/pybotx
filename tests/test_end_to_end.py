from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from loguru import logger
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    IncomingMessage,
    build_accepted_response,
    build_bot_disabled_response,
)
from tests.client.conftest import log_request, log_response

# - pybotx -
collector = HandlerCollector()


@collector.command("/debug", description="Simple debug command")
async def debug_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.send(
        "Works!",
        bot_id=message.bot_id,
        chat_id=message.chat.id,
        metadata={"foo": "bar"},
    )


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccount(
            host="cts.example.com",
            bot_id=UUID("bc7f96e2-91a5-5de4-8bde-23765450cac8"),
            secret_key="secret",
        ),
    ],
    httpx_client=httpx.AsyncClient(
        event_hooks={"request": [log_request], "response": [log_response]},
    ),
)


# - Starlette -
async def command_handler(request: Request) -> JSONResponse:
    try:
        bot.async_execute_raw_bot_command(await request.json())
    except ValueError:
        error_label = "Bot command validation error"
        logger.exception(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    return JSONResponse(build_accepted_response(), status_code=HTTPStatus.ACCEPTED)


async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(dict(request.query_params))
    return JSONResponse(status)


async def callback_handler(request: Request) -> JSONResponse:
    logger.info(await request.json())
    return JSONResponse(build_accepted_response(), status_code=HTTPStatus.ACCEPTED)


app = Starlette(
    routes=[
        Route("/command", endpoint=command_handler, methods=["POST"]),
        Route("/status", endpoint=status_handler, methods=["GET"]),
        Route("/notification/callback", endpoint=callback_handler, methods=["POST"]),
    ],
    on_startup=[bot.startup],
    on_shutdown=[bot.shutdown],
)


# - tests -
@pytest.fixture
def test_client(mock_authorization: None) -> TestClient:
    return TestClient(app)


def test__web_app__bot_status(
    test_client: TestClient,
) -> None:
    response = test_client.get(
        "/status",
        params={
            "bot_id": "34477998-c8c7-53e9-aa4b-66ea5182dc3f",
            "chat_type": "chat",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
        },
    )
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
    test_client: TestClient,
) -> None:
    payload = {
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
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
    response = test_client.post(
        "/command",
        json=payload,
    )

    assert response.status_code == HTTPStatus.ACCEPTED


def test__web_app__disabled_bot_response(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/command",
        json={"incorrect": "request"},
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {
        "error_data": {"status_message": "Bot command validation error"},
        "errors": [],
        "reason": "bot_disabled",
    }
