import importlib
import json
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pybotx import (
    Bot,
    BotAccountWithSecret,
    FastAPIBotAppConfig,
    HandlerCollector,
    create_fastapi_bot_app,
    setup_fastapi_bot,
)
from pybotx.bot.exceptions import UnknownBotAccountError, UnverifiedRequestError
from pybotx.integrations import fastapi as fastapi_adapter

prometheus_client = pytest.importorskip("prometheus_client")
CollectorRegistry = prometheus_client.CollectorRegistry


def test__create_fastapi_bot_app__wires_metrics_and_health_routes(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )
    registry = CollectorRegistry()

    app = create_fastapi_bot_app(
        bot=bot,
        config=FastAPIBotAppConfig(
            verify_request=False,
            metrics_path="/metrics",
        ),
        metrics_registry=registry,
    )

    with TestClient(app) as test_client:
        health_response = test_client.get("/health/")
        readiness_response = test_client.get("/health/ready")
        metrics_response = test_client.get("/metrics")

    assert health_response.status_code == 200
    assert readiness_response.status_code == 200
    assert metrics_response.status_code == 200
    assert metrics_response.headers["content-type"].startswith("text/plain")


def test__create_fastapi_bot_app__stores_extra_app_state(
    bot_account: BotAccountWithSecret,
) -> None:
    container = SimpleNamespace(name="container")
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    app = create_fastapi_bot_app(
        bot=bot,
        config=FastAPIBotAppConfig(verify_request=False),
        app_state={"container": container},
    )

    assert app.state.bot is bot
    assert app.state.container is container
    assert app.state.healthcheck is not None


def test__fastapi_bot_app_config__duplicate_path_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate FastAPI route path"):
        FastAPIBotAppConfig(
            command_path="/command",
            status_path="/command",
        )


def test__fastapi_bot_app_config__relative_path_rejected() -> None:
    with pytest.raises(ValueError, match="should start"):
        FastAPIBotAppConfig(command_path="command")


def test__create_fastapi_bot_app__metrics_registry_required(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    with pytest.raises(ValueError, match="metrics_registry"):
        create_fastapi_bot_app(
            bot=bot,
            config=FastAPIBotAppConfig(
                verify_request=False,
                metrics_path="/metrics",
            ),
        )


def test__create_fastapi_bot_app__reserved_app_state_keys_rejected(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    with pytest.raises(ValueError, match="reserved state keys"):
        create_fastapi_bot_app(
            bot=bot,
            config=FastAPIBotAppConfig(verify_request=False),
            app_state={"bot": object()},
        )


def test__setup_fastapi_bot__configures_existing_app(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )
    app = FastAPI()

    setup_fastapi_bot(
        app,
        bot=bot,
        config=FastAPIBotAppConfig(verify_request=False, healthcheck_prefix=None),
    )

    with TestClient(app) as test_client:
        response = test_client.get(
            "/status",
            params={
                "bot_id": str(bot_account.id),
                "chat_type": "chat",
                "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            },
        )

    assert response.status_code == 200


def test__setup_fastapi_bot__rejects_healthcheck_when_disabled(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    with pytest.raises(ValueError, match="healthcheck"):
        setup_fastapi_bot(
            FastAPI(),
            bot=bot,
            config=FastAPIBotAppConfig(healthcheck_prefix=None),
            healthcheck=object(),  # type: ignore[arg-type]
        )


class _Request:
    headers = {"authorization": "Bearer token"}
    query_params = {"bot_id": "value"}

    async def json(self) -> dict[str, str]:
        return {"payload": "value"}


class _ResponsePayload:
    def jsonable_dict(self) -> dict[str, str]:
        return {"result": "ok"}


class _RouteBot:
    def __init__(self) -> None:
        self.command_error: Exception | None = None
        self.status_error: Exception | None = None
        self.callback_error: Exception | None = None
        self.smartapp_error: Exception | None = None

    async def startup(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    def async_execute_raw_bot_command(self, *_args: Any, **_kwargs: Any) -> None:
        if self.command_error is not None:
            raise self.command_error

    async def raw_get_status(self, *_args: Any, **_kwargs: Any) -> dict[str, str]:
        if self.status_error is not None:
            raise self.status_error
        return {"status": "ok"}

    async def set_raw_botx_method_result(self, *_args: Any, **_kwargs: Any) -> None:
        if self.callback_error is not None:
            raise self.callback_error

    async def sync_execute_raw_smartapp_event(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> _ResponsePayload:
        if self.smartapp_error is not None:
            raise self.smartapp_error
        return _ResponsePayload()


def _endpoint(app: FastAPI, path: str) -> Any:
    return next(route.endpoint for route in app.routes if getattr(route, "path", None) == path)


@pytest.mark.parametrize(
    ("route", "method", "error", "status_code"),
    [
        ("/command", "command_error", ValueError(), 503),
        ("/command", "command_error", UnknownBotAccountError(UUID(int=1)), 503),
        ("/command", "command_error", UnverifiedRequestError("bad token"), 401),
        ("/status", "status_error", ValueError(), 503),
        ("/status", "status_error", UnknownBotAccountError(UUID(int=2)), 503),
        ("/status", "status_error", UnverifiedRequestError("bad token"), 401),
        ("/callback", "callback_error", UnverifiedRequestError("bad token"), 401),
        ("/smartapp", "smartapp_error", ValueError(), 503),
        ("/smartapp", "smartapp_error", UnknownBotAccountError(UUID(int=3)), 503),
        ("/smartapp", "smartapp_error", UnverifiedRequestError("bad token"), 401),
    ],
)
async def test__fastapi_handlers__map_domain_errors(
    route: str,
    method: str,
    error: Exception,
    status_code: int,
) -> None:
    bot = _RouteBot()
    setattr(bot, method, error)
    app = FastAPI()
    setup_fastapi_bot(
        app,
        bot=bot,  # type: ignore[arg-type]
        config=FastAPIBotAppConfig(
            callback_path="/callback",
            smartapp_request_path="/smartapp",
            healthcheck_prefix=None,
            trusted_issuers=frozenset({"trusted.example"}),
        ),
    )

    response = await _endpoint(app, route)(_Request())

    assert response.status_code == status_code


async def test__fastapi_smartapp_handler__returns_domain_response() -> None:
    bot = _RouteBot()
    app = FastAPI()
    setup_fastapi_bot(
        app,
        bot=bot,  # type: ignore[arg-type]
        config=FastAPIBotAppConfig(
            smartapp_request_path="/smartapp",
            healthcheck_prefix=None,
        ),
    )

    response = await _endpoint(app, "/smartapp")(_Request())

    assert response.status_code == 200
    assert json.loads(response.body) == {"result": "ok"}


@pytest.mark.parametrize("missing_module", ["fastapi", "fastapi.responses"])
def test__import_fastapi_runtime__reports_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
    missing_module: str,
) -> None:
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == missing_module:
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    with pytest.raises(RuntimeError, match="requires `fastapi`"):
        fastapi_adapter._import_fastapi_runtime()


def test__build_metrics_runtime__reports_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "prometheus_client":
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    with pytest.raises(RuntimeError, match="prometheus-client"):
        fastapi_adapter._build_metrics_runtime()
