from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from pybotx.application.bot import Bot
from pybotx.domain.errors import UnverifiedRequestError
from pybotx.presentation.api.responses.command_accepted import (
    build_command_accepted_response,
)
from pybotx.presentation.raw_handlers import (
    async_execute_raw_bot_command,
    raw_get_status,
    set_raw_botx_method_result,
    sync_execute_raw_smartapp_event,
)
from pybotx.presentation.webhook_utils import map_botx_exception


class FastAPIAdapter:
    """FastAPI integration for BotX webhook endpoints."""

    def __init__(
        self,
        bot: Bot,
        *,
        verify_requests: bool = True,
        command_path: str = "/command",
        smartapp_path: str = "/smartapps/request",
        status_path: str = "/status",
        status_unverified_path: str = "/status__unverified_request",
        callback_path: str = "/notification/callback",
    ) -> None:
        self._bot = bot
        self._verify_requests = verify_requests
        self._paths = {
            "command": command_path,
            "smartapp": smartapp_path,
            "status": status_path,
            "status_unverified": status_unverified_path,
            "callback": callback_path,
        }
        self._router = APIRouter()
        self._setup_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    def _setup_routes(self) -> None:
        router = self._router

        @router.post(self._paths["command"])  # type: ignore[misc]
        async def command_handler(request: Request) -> JSONResponse:
            try:
                async_execute_raw_bot_command(
                    self._bot,
                    await request.json(),
                    verify_request=self._verify_requests,
                    request_headers=request.headers,
                )
            except Exception as exc:
                mapped = map_botx_exception(
                    exc,
                    validation_label="Bot command validation error",
                )
                if mapped is None:
                    raise
                status_code, payload = mapped
                return JSONResponse(payload, status_code=status_code)

            return JSONResponse(
                build_command_accepted_response(),
                status_code=HTTPStatus.ACCEPTED,
            )

        @router.post(self._paths["smartapp"])  # type: ignore[misc]
        async def sync_smartapp_event_handler(request: Request) -> JSONResponse:
            try:
                response = await sync_execute_raw_smartapp_event(
                    self._bot,
                    await request.json(),
                    verify_request=self._verify_requests,
                    request_headers=request.headers,
                )
            except Exception as exc:
                mapped = map_botx_exception(
                    exc,
                    validation_label="Bot command validation error",
                )
                if mapped is None:
                    raise
                status_code, payload = mapped
                return JSONResponse(payload, status_code=status_code)

            return JSONResponse(response.jsonable_dict(), status_code=HTTPStatus.OK)

        @router.get(self._paths["status"])  # type: ignore[misc]
        async def status_handler(request: Request) -> JSONResponse:
            status = await raw_get_status(
                self._bot,
                dict(request.query_params),
                verify_request=self._verify_requests,
                request_headers=request.headers,
            )
            return JSONResponse(status)

        @router.get(self._paths["status_unverified"])  # type: ignore[misc]
        async def status_handler_unverified(request: Request) -> JSONResponse:
            try:
                status = await raw_get_status(
                    self._bot,
                    dict(request.query_params),
                    request_headers=request.headers,
                )
            except UnverifiedRequestError as exc:
                mapped = map_botx_exception(
                    exc,
                    validation_label="Status request validation error",
                )
                assert mapped is not None
                status_code, payload = mapped
                return JSONResponse(payload, status_code=status_code)
            return JSONResponse(status)

        @router.post(self._paths["callback"])  # type: ignore[misc]
        async def callback_handler(request: Request) -> JSONResponse:
            await set_raw_botx_method_result(
                self._bot,
                await request.json(),
                verify_request=self._verify_requests,
                request_headers=request.headers,
            )
            return JSONResponse(
                build_command_accepted_response(),
                status_code=HTTPStatus.ACCEPTED,
            )


def build_fastapi_router(bot: Bot, *, verify_requests: bool = True) -> APIRouter:
    """Compatibility helper to build APIRouter without instantiating adapter."""
    return FastAPIAdapter(bot, verify_requests=verify_requests).router
