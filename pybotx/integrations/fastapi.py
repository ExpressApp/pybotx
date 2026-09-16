from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
import importlib
from typing import TYPE_CHECKING, Any, cast

from pybotx.bot.api.responses.bot_disabled import build_bot_disabled_response
from pybotx.bot.api.responses.command_accepted import build_command_accepted_response
from pybotx.bot.api.responses.unverified_request import (
    build_unverified_request_response,
)
from pybotx.bot.bot import Bot
from pybotx.bot.exceptions import UnknownBotAccountError, UnverifiedRequestError
from pybotx.bot.healthcheck import HealthcheckService, setup_healthcheck
from pybotx.logger import logger

if TYPE_CHECKING:
    from fastapi import FastAPI, Request


@dataclass(frozen=True, slots=True)
class FastAPIBotAppConfig:
    command_path: str = "/command"
    status_path: str = "/status"
    callback_path: str = "/notification/callback"
    smartapp_request_path: str | None = None
    metrics_path: str | None = None
    healthcheck_prefix: str | None = "/health"
    verify_request: bool = True
    verify_callback_request: bool = False
    trusted_issuers: frozenset[str] | None = None

    def __post_init__(self) -> None:
        route_paths = {
            "command_path": self.command_path,
            "status_path": self.status_path,
            "callback_path": self.callback_path,
            "smartapp_request_path": self.smartapp_request_path,
            "metrics_path": self.metrics_path,
            "healthcheck_prefix": self.healthcheck_prefix,
        }

        seen_paths: set[str] = set()
        for field_name, path in route_paths.items():
            if path is None:
                continue
            if not path.startswith("/"):
                raise ValueError(f"`{field_name}` should start with '/'")
            if path in seen_paths:
                raise ValueError(f"Duplicate FastAPI route path `{path}`")
            seen_paths.add(path)


def create_fastapi_bot_app(
    *,
    bot: Bot,
    title: str = "pybotx",
    openapi_url: str | None = "/openapi.json",
    docs_url: str | None = "/docs",
    redoc_url: str | None = "/redoc",
    config: FastAPIBotAppConfig | None = None,
    metrics_registry: Any | None = None,
    healthcheck: HealthcheckService | None = None,
    app_state: Mapping[str, Any] | None = None,
) -> "FastAPI":
    fastapi_module, _, _, _ = _import_fastapi_runtime()
    fastapi_cls = getattr(fastapi_module, "FastAPI")

    app = fastapi_cls(
        title=title,
        openapi_url=openapi_url,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    setup_fastapi_bot(
        app,
        bot=bot,
        config=config,
        metrics_registry=metrics_registry,
        healthcheck=healthcheck,
        app_state=app_state,
    )
    return cast("FastAPI", app)


def setup_fastapi_bot(
    app: "FastAPI",
    *,
    bot: Bot,
    config: FastAPIBotAppConfig | None = None,
    metrics_registry: Any | None = None,
    healthcheck: HealthcheckService | None = None,
    app_state: Mapping[str, Any] | None = None,
) -> HealthcheckService | None:
    config = config or FastAPIBotAppConfig()
    _, request_cls, response_cls, json_response_cls = _import_fastapi_runtime()
    globals()["Request"] = request_cls

    if config.metrics_path is not None and metrics_registry is None:
        raise ValueError(
            "`metrics_registry` should be provided when `metrics_path` is configured",
        )
    if config.healthcheck_prefix is None and healthcheck is not None:
        raise ValueError(
            "`healthcheck` can't be passed when `healthcheck_prefix` is disabled",
        )
    reserved_state_keys = {"bot", "healthcheck"}
    if app_state is not None and reserved_state_keys.intersection(app_state):
        reserved_keys = ", ".join(sorted(reserved_state_keys.intersection(app_state)))
        raise ValueError(
            f"`app_state` can't override reserved state keys: {reserved_keys}",
        )

    app.state.bot = bot
    for state_key, state_value in (app_state or {}).items():
        setattr(app.state, state_key, state_value)

    app.add_event_handler("startup", bot.startup)
    app.add_event_handler("shutdown", bot.shutdown)

    if config.healthcheck_prefix is not None:
        healthcheck = setup_healthcheck(
            app,
            healthcheck=healthcheck,
            prefix=config.healthcheck_prefix,
        )
        app.state.healthcheck = healthcheck

    @app.post(config.command_path)
    async def command_handler(request: Request) -> Any:
        try:
            bot.async_execute_raw_bot_command(
                await request.json(),
                verify_request=config.verify_request,
                request_headers=request.headers,
                trusted_issuers=_trusted_issuers(config),
            )
        except ValueError as exc:
            return _build_disabled_response(
                str(exc) or "Bot command validation error",
                json_response_cls,
            )
        except UnknownBotAccountError as exc:
            error_label = f"No credentials for bot {exc.bot_id}"
            logger.warning(error_label)
            return _build_disabled_response(error_label, json_response_cls)
        except UnverifiedRequestError as exc:
            return _build_unverified_response(str(exc), json_response_cls)

        return json_response_cls(
            build_command_accepted_response(),
            status_code=HTTPStatus.ACCEPTED,
        )

    @app.get(config.status_path)
    async def status_handler(request: Request) -> Any:
        try:
            status = await bot.raw_get_status(
                dict(request.query_params),
                verify_request=config.verify_request,
                request_headers=request.headers,
                trusted_issuers=_trusted_issuers(config),
            )
        except ValueError as exc:
            return _build_disabled_response(
                str(exc) or "Status request validation error",
                json_response_cls,
            )
        except UnknownBotAccountError as exc:
            error_label = f"No credentials for bot {exc.bot_id}"
            logger.warning(error_label)
            return _build_disabled_response(error_label, json_response_cls)
        except UnverifiedRequestError as exc:
            return _build_unverified_response(str(exc), json_response_cls)

        return json_response_cls(status, status_code=HTTPStatus.OK)

    @app.post(config.callback_path)
    async def callback_handler(request: Request) -> Any:
        try:
            await bot.set_raw_botx_method_result(
                await request.json(),
                verify_request=config.verify_callback_request,
                request_headers=request.headers,
                trusted_issuers=_trusted_issuers(config),
            )
        except UnverifiedRequestError as exc:
            return _build_unverified_response(str(exc), json_response_cls)

        return json_response_cls(
            build_command_accepted_response(),
            status_code=HTTPStatus.ACCEPTED,
        )

    if config.smartapp_request_path is not None:

        @app.post(config.smartapp_request_path)
        async def sync_smartapp_event_handler(request: Request) -> Any:
            try:
                response = await bot.sync_execute_raw_smartapp_event(
                    await request.json(),
                    verify_request=config.verify_request,
                    request_headers=request.headers,
                    trusted_issuers=_trusted_issuers(config),
                )
            except ValueError as exc:
                return _build_disabled_response(
                    str(exc) or "Sync smartapp event validation error",
                    json_response_cls,
                )
            except UnknownBotAccountError as exc:
                error_label = f"No credentials for bot {exc.bot_id}"
                logger.warning(error_label)
                return _build_disabled_response(error_label, json_response_cls)
            except UnverifiedRequestError as exc:
                return _build_unverified_response(str(exc), json_response_cls)

            return json_response_cls(response.jsonable_dict(), status_code=HTTPStatus.OK)

    if config.metrics_path is not None:
        generate_latest, content_type = _build_metrics_runtime()

        @app.get(config.metrics_path)
        async def metrics_handler() -> Any:
            return response_cls(
                content=generate_latest(metrics_registry),
                media_type=content_type,
            )

    return healthcheck


def _build_disabled_response(error_label: str, json_response_cls: Any) -> Any:
    logger.exception(error_label)
    return json_response_cls(
        build_bot_disabled_response(error_label),
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
    )


def _build_unverified_response(error_label: str, json_response_cls: Any) -> Any:
    logger.warning(error_label)
    return json_response_cls(
        build_unverified_request_response(status_message=error_label),
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def _trusted_issuers(config: FastAPIBotAppConfig) -> set[str] | None:
    if config.trusted_issuers is None:
        return None
    return set(config.trusted_issuers)


def _build_metrics_runtime() -> tuple[Any, str]:
    try:
        prometheus_client = importlib.import_module("prometheus_client")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FastAPI metrics endpoint requires `prometheus-client`. "
            "Install with `uv add prometheus-client`.",
        ) from exc

    return (
        getattr(prometheus_client, "generate_latest"),
        getattr(prometheus_client, "CONTENT_TYPE_LATEST"),
    )


def _import_fastapi_runtime() -> tuple[Any, Any, Any, Any]:
    try:
        fastapi_module = importlib.import_module("fastapi")
        fastapi_responses_module = importlib.import_module("fastapi.responses")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FastAPI integration requires `fastapi`. "
            "Install with `uv add fastapi`.",
        ) from exc

    return (
        fastapi_module,
        getattr(fastapi_module, "Request"),
        getattr(fastapi_module, "Response"),
        getattr(fastapi_responses_module, "JSONResponse"),
    )
