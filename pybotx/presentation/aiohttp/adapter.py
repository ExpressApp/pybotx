from __future__ import annotations

from http import HTTPStatus

from aiohttp import web

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
from pybotx.presentation.webhook_utils import map_botx_exception


class AiohttpAdapter:
    """aiohttp integration for BotX webhook endpoints."""

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

    def register(self, app: web.Application) -> None:
        app.router.add_post(self._paths["command"], self._command_handler)
        app.router.add_post(self._paths["smartapp"], self._smartapp_handler)
        app.router.add_get(self._paths["status"], self._status_handler)
        app.router.add_get(
            self._paths["status_unverified"],
            self._status_handler_unverified,
        )
        app.router.add_post(self._paths["callback"], self._callback_handler)

    async def _command_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
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
            status_code, payload = mapped
            return web.json_response(payload, status=status_code)

        return web.json_response(
            build_command_accepted_response(),
            status=HTTPStatus.ACCEPTED,
        )

    async def _smartapp_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
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
            status_code, payload = mapped
            return web.json_response(payload, status=status_code)

        return web.json_response(response.jsonable_dict(), status=HTTPStatus.OK)

    async def _status_handler(self, request: web.Request) -> web.Response:
        status = await raw_get_status(
            self._bot,
            dict(request.query),
            verify_request=self._verify_requests,
            request_headers=request.headers,
        )
        return web.json_response(status)

    async def _status_handler_unverified(self, request: web.Request) -> web.Response:
        try:
            status = await raw_get_status(
                self._bot,
                dict(request.query),
                request_headers=request.headers,
            )
        except Exception as exc:
            mapped = map_botx_exception(
                exc,
                validation_label="Status request validation error",
            )
            if mapped is None:
                raise
            status_code, payload = mapped
            return web.json_response(payload, status=status_code)
        return web.json_response(status)

    async def _callback_handler(self, request: web.Request) -> web.Response:
        await set_raw_botx_method_result(
            self._bot,
            await request.json(),
            verify_request=self._verify_requests,
            request_headers=request.headers,
        )
        return web.json_response(
            build_command_accepted_response(),
            status=HTTPStatus.ACCEPTED,
        )


def build_aiohttp_app(bot: Bot, *, verify_requests: bool = True) -> web.Application:
    """Compatibility helper to build aiohttp app without direct adapter usage."""
    adapter = AiohttpAdapter(bot, verify_requests=verify_requests)
    app = web.Application()
    adapter.register(app)

    async def _on_startup(_app: web.Application) -> None:
        await bot.startup()

    async def _on_shutdown(_app: web.Application) -> None:
        await bot.shutdown()

    app.on_startup.append(_on_startup)
    app.on_shutdown.append(_on_shutdown)
    return app
