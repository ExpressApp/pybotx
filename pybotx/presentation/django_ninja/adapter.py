from __future__ import annotations

from http import HTTPStatus
from typing import Any

from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from pybotx.application.bot import Bot
from pybotx.presentation.api.responses.command_accepted import (
    build_command_accepted_response,
)
from pybotx.presentation.raw_handlers import (
    async_execute_raw_bot_command,
    raw_get_status,
    set_raw_botx_method_result,
    sync_execute_raw_smartapp_event,
)
from pybotx.presentation.webhook_utils import map_botx_exception, parse_json_body


def _parse_json(body: bytes) -> dict[str, Any]:
    return parse_json_body(body)


class DjangoNinjaAdapter:
    """Django Ninja integration for BotX webhook endpoints."""

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
        self._router = Router()
        self._setup_routes()

    @property
    def router(self) -> Router:
        return self._router

    def _setup_routes(self) -> None:
        router = self._router

        @router.post(  # type: ignore[misc]
            self._paths["command"],
            response={202: dict, 401: dict, 503: dict},
        )
        @csrf_exempt
        async def command_handler(request) -> tuple[int, dict[str, Any]]:
            try:
                payload = parse_json_body(request.body)
                async_execute_raw_bot_command(
                    self._bot,
                    payload,
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
                return mapped

            return (
                HTTPStatus.ACCEPTED,
                build_command_accepted_response(),
            )

        @router.post(  # type: ignore[misc]
            self._paths["smartapp"],
            response={200: dict, 401: dict, 503: dict},
        )
        @csrf_exempt
        async def smartapp_handler(request) -> tuple[int, dict[str, Any]]:
            try:
                payload = parse_json_body(request.body)
                response = await sync_execute_raw_smartapp_event(
                    self._bot,
                    payload,
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
                return mapped

            return (HTTPStatus.OK, response.jsonable_dict())

        @router.get(self._paths["status"], response=dict)  # type: ignore[misc]
        @csrf_exempt
        async def status_handler(request) -> dict[str, Any]:
            status = await raw_get_status(
                self._bot,
                request.GET.dict(),
                verify_request=self._verify_requests,
                request_headers=request.headers,
            )
            return status

        @router.get(  # type: ignore[misc]
            self._paths["status_unverified"],
            response={200: dict, 401: dict},
        )
        @csrf_exempt
        async def status_handler_unverified(request) -> tuple[int, dict[str, Any]]:
            try:
                status = await raw_get_status(
                    self._bot,
                    request.GET.dict(),
                    request_headers=request.headers,
                )
            except Exception as exc:
                mapped = map_botx_exception(
                    exc,
                    validation_label="Status request validation error",
                )
                if mapped is None:
                    raise
                return mapped
            return (HTTPStatus.OK, status)

        @router.post(self._paths["callback"], response={202: dict})  # type: ignore[misc]
        @csrf_exempt
        async def callback_handler(request) -> tuple[int, dict[str, Any]]:
            await set_raw_botx_method_result(
                self._bot,
                parse_json_body(request.body),
                verify_request=self._verify_requests,
                request_headers=request.headers,
            )
            return (
                HTTPStatus.ACCEPTED,
                build_command_accepted_response(),
            )


def build_django_ninja_router(
    bot: Bot,
    *,
    verify_requests: bool = True,
) -> Router:
    """Compatibility helper to build Router without instantiating adapter."""
    return DjangoNinjaAdapter(bot, verify_requests=verify_requests).router
