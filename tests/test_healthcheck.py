import asyncio
from datetime import datetime
from http import HTTPStatus
from typing import Any, Literal, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pybotx import (
    HealthcheckService,
    ReadinessCheck,
    ReadinessCheckResult,
    build_healthcheck_router,
    setup_healthcheck,
)


def _assert_utc_timestamp(timestamp: str) -> None:
    parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert parsed_timestamp.tzinfo is not None


def test__healthcheck_routes__not_connected_by_default() -> None:
    app = FastAPI()

    with TestClient(app) as test_client:
        response = test_client.get("/health/")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test__setup_healthcheck__liveness_success() -> None:
    app = FastAPI()
    setup_healthcheck(app)

    with TestClient(app) as test_client:
        response = test_client.get("/health/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "ok"
    _assert_utc_timestamp(response.json()["timestamp"])


def test__healthcheck_liveness__fatal_state_and_reset() -> None:
    app = FastAPI()
    healthcheck = setup_healthcheck(app)

    with TestClient(app) as test_client:
        healthcheck.mark_fatal()
        response_with_fatal = test_client.get("/health/")
        healthcheck.clear_fatal()
        response_after_reset = test_client.get("/health/")

    assert response_with_fatal.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response_with_fatal.json()["status"] == "fail"
    assert response_after_reset.status_code == HTTPStatus.OK
    assert response_after_reset.json()["status"] == "ok"


def test__healthcheck_readiness__initialization_failed() -> None:
    app = FastAPI()
    healthcheck = setup_healthcheck(app)

    with TestClient(app) as test_client:
        healthcheck.mark_uninitialized()
        response = test_client.get("/health/ready")

    response_payload = response.json()
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response_payload == {
        "status": "fail",
        "time": response_payload["time"],
        "checks": {
            "initialization": {
                "status": "fail",
                "reason": "application isn't initialized",
            },
        },
    }
    _assert_utc_timestamp(response_payload["time"])


def test__healthcheck_readiness__critical_and_non_critical_statuses() -> None:
    async def critical_check() -> bool:
        return False

    async def non_critical_check() -> Literal["degraded"]:
        return "degraded"

    app = FastAPI()
    setup_healthcheck(
        app,
        healthcheck=HealthcheckService(
            readiness_checks=[
                ReadinessCheck(name="db", check=critical_check, critical=True),
                ReadinessCheck(
                    name="ext_api",
                    check=non_critical_check,
                    critical=False,
                    timeout_seconds=None,
                ),
            ],
        ),
    )

    with TestClient(app) as test_client:
        response = test_client.get("/health/ready")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json()["status"] == "fail"
    assert response.json()["checks"]["db"]["status"] == "fail"
    assert response.json()["checks"]["ext_api"]["status"] == "degraded"


def test__healthcheck_readiness__non_critical_fail_is_degraded() -> None:
    async def redis_check() -> ReadinessCheckResult:
        return ReadinessCheckResult(status="fail", reason="timeout", latency_ms=200)

    app = FastAPI()
    setup_healthcheck(
        app,
        healthcheck=HealthcheckService(
            readiness_checks=[
                ReadinessCheck(name="redis", check=redis_check, critical=False),
            ],
        ),
    )

    with TestClient(app) as test_client:
        response = test_client.get("/health/ready")

    response_payload = response.json()
    assert response.status_code == HTTPStatus.OK
    assert response_payload == {
        "status": "degraded",
        "time": response_payload["time"],
        "checks": {
            "initialization": {"status": "ok"},
            "redis": {"status": "fail", "reason": "timeout", "latency_ms": 200},
        },
    }


def test__healthcheck_readiness__timeout_and_exception() -> None:
    async def timeout_check() -> bool:
        await asyncio.sleep(0.02)
        return True

    async def broken_check() -> Any:
        return 1

    app = FastAPI()
    setup_healthcheck(
        app,
        healthcheck=HealthcheckService(
            readiness_checks=[
                ReadinessCheck(
                    name="timeout_check",
                    check=timeout_check,
                    critical=False,
                    timeout_seconds=0.001,
                ),
                ReadinessCheck(name="broken_check", check=cast(Any, broken_check)),
            ],
        ),
    )

    with TestClient(app) as test_client:
        response = test_client.get("/health/ready")

    response_payload = response.json()
    timeout_result = response_payload["checks"]["timeout_check"]
    broken_result = response_payload["checks"]["broken_check"]
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response_payload["status"] == "fail"
    assert timeout_result["status"] == "fail"
    assert timeout_result["reason"] == "timeout"
    assert isinstance(timeout_result["latency_ms"], int)
    assert broken_result["status"] == "fail"
    assert "TypeError" in broken_result["reason"]


def test__healthcheck_readiness__without_initialization_check() -> None:
    app = FastAPI()
    healthcheck = HealthcheckService(
        readiness_checks=[
            ReadinessCheck(name="db", check=lambda: True),
            ReadinessCheck(name="cache", check=lambda: ReadinessCheckResult(status="ok")),
        ],
        include_initialization_check=False,
    )
    healthcheck.mark_fatal("fatal app state")
    setup_healthcheck(app, healthcheck=healthcheck)

    with TestClient(app) as test_client:
        response = test_client.get("/health/ready")

    response_payload = response.json()
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response_payload["status"] == "fail"
    assert response_payload["checks"]["application"] == {
        "status": "fail",
        "reason": "fatal app state",
    }
    assert response_payload["checks"]["db"]["status"] == "ok"
    assert response_payload["checks"]["cache"]["status"] == "ok"


def test__build_healthcheck_router__works_with_manual_include() -> None:
    app = FastAPI()
    healthcheck = HealthcheckService()
    app.include_router(
        build_healthcheck_router(healthcheck=healthcheck),
        prefix="/health",
    )

    with TestClient(app) as test_client:
        response = test_client.get("/health/ready")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["checks"]["initialization"]["status"] == "ok"


def test__healthcheck_validation() -> None:
    with pytest.raises(ValueError, match="prefix"):
        setup_healthcheck(FastAPI(), prefix="health")

    with pytest.raises(ValueError, match="name should not be empty"):
        ReadinessCheck(name="", check=lambda: True)

    with pytest.raises(ValueError, match="timeout should be greater than 0"):
        ReadinessCheck(name="db", check=lambda: True, timeout_seconds=0)

    with pytest.raises(ValueError, match="status should be one of"):
        ReadinessCheckResult(status="bad")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="latency should be greater or equal to 0"):
        ReadinessCheckResult(status="ok", latency_ms=-1)

    healthcheck = HealthcheckService()
    healthcheck.add_readiness_check(ReadinessCheck(name="db", check=lambda: True))
    with pytest.raises(ValueError, match="already exists"):
        healthcheck.add_readiness_check(ReadinessCheck(name="db", check=lambda: True))
