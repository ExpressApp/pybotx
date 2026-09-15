import asyncio
import inspect
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Literal, TypeAlias
from collections.abc import Awaitable, Callable, Sequence

if TYPE_CHECKING:
    from fastapi import APIRouter, FastAPI

HealthStatus: TypeAlias = Literal["ok", "degraded", "fail"]

_ALLOWED_HEALTH_STATUSES = {"ok", "degraded", "fail"}


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _format_utc_timestamp(now: datetime) -> str:
    return now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


@dataclass(frozen=True, slots=True)
class ReadinessCheckResult:
    status: HealthStatus
    reason: str | None = None
    latency_ms: int | None = None

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_HEALTH_STATUSES:
            raise ValueError(
                "Readiness check status should be one of: "
                f"{', '.join(sorted(_ALLOWED_HEALTH_STATUSES))}",
            )
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("Readiness check latency should be greater or equal to 0")


ReadinessCheckValue: TypeAlias = ReadinessCheckResult | HealthStatus | bool
ReadinessCheckFunc: TypeAlias = Callable[
    [],
    ReadinessCheckValue | Awaitable[ReadinessCheckValue],
]


@dataclass(frozen=True, slots=True)
class ReadinessCheck:
    name: str
    check: ReadinessCheckFunc
    critical: bool = True
    timeout_seconds: float | None = 1.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Readiness check name should not be empty")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("Readiness check timeout should be greater than 0")


class HealthcheckService:
    def __init__(
        self,
        *,
        readiness_checks: Sequence[ReadinessCheck] | None = None,
        include_initialization_check: bool = True,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._readiness_checks: list[ReadinessCheck] = []
        self._include_initialization_check = include_initialization_check
        self._now_provider = now_provider or _utc_now
        self._initialized = False
        self._fatal_error: str | None = None

        for readiness_check in readiness_checks or ():
            self.add_readiness_check(readiness_check)

    def add_readiness_check(self, readiness_check: ReadinessCheck) -> None:
        if any(existing.name == readiness_check.name for existing in self._readiness_checks):
            raise ValueError(
                f"Readiness check with name `{readiness_check.name}` already exists",
            )
        self._readiness_checks.append(readiness_check)

    def mark_initialized(self) -> None:
        self._initialized = True

    def mark_uninitialized(self) -> None:
        self._initialized = False

    def mark_fatal(self, reason: str | None = None) -> None:
        self._fatal_error = reason or "fatal application state"

    def clear_fatal(self) -> None:
        self._fatal_error = None

    async def get_liveness(self) -> tuple[HTTPStatus, dict[str, str]]:
        timestamp = _format_utc_timestamp(self._now_provider())
        if self._fatal_error is not None:
            return (
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"status": "fail", "timestamp": timestamp},
            )
        return HTTPStatus.OK, {"status": "ok", "timestamp": timestamp}

    async def get_readiness(self) -> tuple[HTTPStatus, dict[str, Any]]:
        has_critical_failures = False
        has_degraded_checks = False
        checks_payload: dict[str, dict[str, Any]] = {}

        if self._include_initialization_check:
            init_check_payload: dict[str, Any] = {
                "status": "ok" if self._initialized else "fail",
            }
            if not self._initialized:
                init_check_payload["reason"] = "application isn't initialized"
                has_critical_failures = True
            checks_payload["initialization"] = init_check_payload

        if self._fatal_error is not None:
            checks_payload["application"] = {
                "status": "fail",
                "reason": self._fatal_error,
            }
            has_critical_failures = True

        if self._readiness_checks:
            readiness_results = await asyncio.gather(
                *(
                    self._execute_readiness_check(readiness_check)
                    for readiness_check in self._readiness_checks
                ),
            )

            for readiness_check, readiness_result in readiness_results:
                checks_payload[readiness_check.name] = self._result_to_payload(
                    readiness_result,
                )

                if readiness_result.status == "fail" and readiness_check.critical:
                    has_critical_failures = True
                if readiness_result.status != "ok":
                    has_degraded_checks = True

        if has_critical_failures:
            readiness_status: HealthStatus = "fail"
            http_status = HTTPStatus.SERVICE_UNAVAILABLE
        elif has_degraded_checks:
            readiness_status = "degraded"
            http_status = HTTPStatus.OK
        else:
            readiness_status = "ok"
            http_status = HTTPStatus.OK

        payload: dict[str, Any] = {
            "status": readiness_status,
            "time": _format_utc_timestamp(self._now_provider()),
            "checks": checks_payload,
        }

        return http_status, payload

    async def _execute_readiness_check(
        self,
        readiness_check: ReadinessCheck,
    ) -> tuple[ReadinessCheck, ReadinessCheckResult]:
        started_at = time.perf_counter()
        try:
            raw_result_or_awaitable = readiness_check.check()

            if inspect.isawaitable(raw_result_or_awaitable):
                if readiness_check.timeout_seconds is None:
                    raw_result = await raw_result_or_awaitable
                else:
                    raw_result = await asyncio.wait_for(
                        raw_result_or_awaitable,
                        timeout=readiness_check.timeout_seconds,
                    )
            else:
                raw_result = raw_result_or_awaitable

            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            result = self._normalize_readiness_result(raw_result, elapsed_ms)
        except asyncio.TimeoutError:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            result = ReadinessCheckResult(
                status="fail",
                reason="timeout",
                latency_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            result = ReadinessCheckResult(
                status="fail",
                reason=f"{type(exc).__name__}: {exc}",
                latency_ms=elapsed_ms,
            )

        return readiness_check, result

    def _normalize_readiness_result(
        self,
        raw_result: ReadinessCheckValue,
        elapsed_ms: int,
    ) -> ReadinessCheckResult:
        if isinstance(raw_result, ReadinessCheckResult):
            if raw_result.latency_ms is not None:
                return raw_result
            return ReadinessCheckResult(
                status=raw_result.status,
                reason=raw_result.reason,
                latency_ms=elapsed_ms,
            )

        if isinstance(raw_result, bool):
            return ReadinessCheckResult(
                status="ok" if raw_result else "fail",
                latency_ms=elapsed_ms,
            )

        if raw_result in _ALLOWED_HEALTH_STATUSES:
            return ReadinessCheckResult(
                status=raw_result,
                latency_ms=elapsed_ms,
            )

        raise TypeError(
            "Unsupported readiness check result type. "
            "Use bool, HealthStatus or ReadinessCheckResult.",
        )

    def _result_to_payload(
        self,
        readiness_result: ReadinessCheckResult,
    ) -> dict[str, Any]:
        result_payload: dict[str, Any] = {
            "status": readiness_result.status,
            "latency_ms": readiness_result.latency_ms,
        }
        if readiness_result.reason is not None:
            result_payload["reason"] = readiness_result.reason

        return result_payload


def build_healthcheck_router(
    *,
    healthcheck: HealthcheckService | None = None,
) -> "APIRouter":
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse

    healthcheck = healthcheck or HealthcheckService()
    router = APIRouter()

    @router.get("/")
    async def health_handler() -> JSONResponse:
        status_code, payload = await healthcheck.get_liveness()
        return JSONResponse(content=payload, status_code=status_code)

    @router.get("/ready")
    async def readiness_handler() -> JSONResponse:
        status_code, payload = await healthcheck.get_readiness()
        return JSONResponse(content=payload, status_code=status_code)

    router.add_event_handler("startup", healthcheck.mark_initialized)
    router.add_event_handler("shutdown", healthcheck.mark_uninitialized)

    return router


def setup_healthcheck(
    app: "FastAPI",
    *,
    healthcheck: HealthcheckService | None = None,
    prefix: str = "/health",
) -> HealthcheckService:
    if not prefix.startswith("/"):
        raise ValueError("Healthcheck prefix should start with '/'")

    healthcheck = healthcheck or HealthcheckService()
    app.include_router(
        build_healthcheck_router(healthcheck=healthcheck),
        prefix=prefix,
    )
    return healthcheck
