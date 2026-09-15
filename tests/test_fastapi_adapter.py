from types import SimpleNamespace

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
