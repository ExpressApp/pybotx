import logging
import pathlib
import random
import string
from typing import Callable, Dict, Optional
from uuid import UUID, uuid4

import pytest
from _pytest.logging import LogCaptureFixture
from httpx import AsyncClient
from loguru import logger
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from botx import CTS, Bot, CTSCredentials, File, Message, ReplyMessage, SystemEventsEnum
from botx.core import BotXAPI
from botx.sync import SyncBot

from .utils import generate_user, generate_username, get_route_path_from_template


@pytest.fixture
def secret() -> str:
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(20, 30))
    )


@pytest.fixture(scope="session")
def host() -> str:
    return "cts.example.com"


@pytest.fixture(scope="session")
def bot_id() -> UUID:
    return uuid4()


@pytest.fixture
def sync_id() -> UUID:
    return uuid4()


@pytest.fixture
def gif_file() -> File:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.gif", "rb") as f:
        return File.from_file(f)


@pytest.fixture
def json_file() -> File:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.json", "r") as f:
        return File.from_file(f)


@pytest.fixture
def png_file() -> File:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.png", "rb") as f:
        return File.from_file(f)


@pytest.fixture
def txt_file() -> File:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.txt", "r") as f:
        return File.from_file(f)


@pytest.fixture
def chat_created_data() -> Dict:
    return {
        "group_chat_id": uuid4(),
        "chat_type": "group_chat",
        "name": "Test Chat",
        "creator": uuid4(),
        "members": [
            {
                "huid": uuid4(),
                "user_kind": random.choice(["user", "botx"]),
                "name": generate_username(),
                "admin": random.choice([True, False]),
            }
            for _ in range(random.randrange(2, 6))
        ],
    }


@pytest.fixture
def message_data(
    bot_id: UUID, sync_id: UUID, host: str, json_file, chat_created_data: Dict
) -> Callable:
    def _create_message_data(
        command: str = "/cmd",
        file: bool = True,
        admin: bool = False,
        chat_creator: bool = False,
    ) -> Dict:
        command_body = {"body": command, "command_type": "user", "data": {}}

        if command == SystemEventsEnum.chat_created.value:
            command_body["data"] = chat_created_data
            command_body["command_type"] = "system"

        data = {
            "bot_id": str(bot_id),
            "command": command_body,
            "file": json_file.dict() if file else None,
            "from": generate_user(host, admin, chat_creator),
            "sync_id": str(sync_id),
        }
        return data

    return _create_message_data


@pytest.fixture
def reply_message(message_data: Callable) -> ReplyMessage:
    return ReplyMessage.from_message("text", Message(**message_data()))


@pytest.fixture
def handler_factory() -> Callable:
    def _create_handler(handler_type: str = "sync") -> Callable:
        if handler_type == "sync":

            def sync_handler(*_) -> None:
                pass

            return sync_handler
        elif handler_type == "async":

            async def async_handler(*_) -> None:
                pass

            return async_handler
        else:
            raise ValueError("handler_type can be only 'sync' or 'async'")

    return _create_handler


@pytest.fixture
def get_botx_api_app() -> Callable:
    async def default_route(*_) -> JSONResponse:
        return JSONResponse({"status": "ok", "result": "result"})

    async def default_error_route(*_) -> JSONResponse:
        return JSONResponse(
            {"status": "error", "message": "error response"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def get_default_route(generate_error_response: bool) -> Callable:
        return default_route if not generate_error_response else default_error_route

    def _get_asgi_app(
        command_route: Optional[Callable] = None,
        notification_route: Optional[Callable] = None,
        file_route: Optional[Callable] = None,
        token_route: Optional[Callable] = None,
        *,
        generate_error_response: bool = False,
    ) -> Starlette:
        app = Starlette()
        app.add_route(
            get_route_path_from_template(BotXAPI.V3.command.url),
            command_route or get_default_route(generate_error_response),
            methods=[BotXAPI.V3.command.method],
        )
        app.add_route(
            get_route_path_from_template(BotXAPI.V3.notification.url),
            notification_route or get_default_route(generate_error_response),
            methods=[BotXAPI.V3.notification.method],
        )
        app.add_route(
            get_route_path_from_template(BotXAPI.V1.file.url),
            file_route or get_default_route(generate_error_response),
            methods=[BotXAPI.V1.file.method],
        )
        app.add_route(
            get_route_path_from_template(BotXAPI.V2.token.url),
            token_route or get_default_route(generate_error_response),
            methods=[BotXAPI.V2.token.method],
        )

        return app

    return _get_asgi_app


@pytest.fixture
def botx_api_app(get_botx_api_app: Callable) -> Starlette:
    return get_botx_api_app()


@pytest.fixture
def botx_error_api_app(get_botx_api_app: Callable) -> Starlette:
    async def route(*_) -> JSONResponse:
        return JSONResponse(
            {"status": "error", "message": "error response"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return get_botx_api_app(*([route] * 4))


@pytest.fixture
def caplog(caplog: LogCaptureFixture) -> LogCaptureFixture:
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def get_bot(get_botx_api_app: Callable, bot_id: UUID, host: str) -> Callable:
    def _get_bot(
        *,
        command_route: Optional[Callable] = None,
        notification_route: Optional[Callable] = None,
        file_route: Optional[Callable] = None,
        token_route: Optional[Callable] = None,
        set_token: bool = False,
        generate_error_response: bool = False,
        create_sync_bot: bool = False,
    ) -> Bot:
        app = get_botx_api_app(
            command_route,
            notification_route,
            file_route,
            token_route,
            generate_error_response=generate_error_response,
        )
        bot = Bot() if not create_sync_bot else SyncBot()
        bot.client.client = AsyncClient(app=app)
        if set_token:
            bot.add_cts(
                CTS(
                    host=host,
                    secret_key="secret",
                    credentials=CTSCredentials(bot_id=bot_id, token="token"),
                )
            )

        return bot

    return _get_bot
