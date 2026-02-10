import importlib
import sys
import types
from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest

from pybotx.domain.errors import UnknownBotAccountError, UnverifiedRequestError
from pybotx.presentation.api.responses.bot_disabled import build_bot_disabled_response
from pybotx.presentation.api.responses.command_accepted import (
    build_command_accepted_response,
)
from pybotx.presentation.api.responses.unverified_request import (
    build_unverified_request_response,
)


class DummyQuery:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def dict(self) -> dict[str, str]:
        return dict(self._data)


class DummyRequest:
    def __init__(
        self,
        *,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
    ) -> None:
        self.body = body
        self.headers = headers or {}
        self.GET = DummyQuery(query or {})


class DummyResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def jsonable_dict(self) -> dict[str, Any]:
        return self._payload


class DummyBot:
    def __init__(self) -> None:
        self.command_payload: dict[str, Any] | None = None
        self.smartapp_payload: dict[str, Any] | None = None
        self.status_payload: dict[str, str] | None = None
        self.callback_payload: dict[str, Any] | None = None
        self.command_error: Exception | None = None
        self.smartapp_error: Exception | None = None
        self.status_error: Exception | None = None

    def async_execute_raw_bot_command(
        self,
        payload: dict[str, Any],
        *,
        verify_request: bool,
        request_headers: dict[str, str],
    ) -> None:
        if self.command_error is not None:
            raise self.command_error
        self.command_payload = payload

    async def sync_execute_raw_smartapp_event(
        self,
        payload: dict[str, Any],
        *,
        verify_request: bool,
        request_headers: dict[str, str],
    ) -> DummyResponse:
        if self.smartapp_error is not None:
            raise self.smartapp_error
        self.smartapp_payload = payload
        return DummyResponse({"status": "ok"})

    async def raw_get_status(
        self,
        query_params: dict[str, str],
        verify_request: bool = True,
        request_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self.status_error is not None:
            raise self.status_error
        self.status_payload = query_params
        return {"status": "ok"}

    async def set_raw_botx_method_result(
        self,
        payload: dict[str, Any],
        *,
        verify_request: bool,
        request_headers: dict[str, str],
    ) -> None:
        self.callback_payload = payload


def _install_django_ninja_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    django_module = types.ModuleType("django")
    django_views = types.ModuleType("django.views")
    django_decorators = types.ModuleType("django.views.decorators")
    django_csrf = types.ModuleType("django.views.decorators.csrf")

    def csrf_exempt(func):  # type: ignore[no-untyped-def]
        return func

    django_csrf.csrf_exempt = csrf_exempt

    monkeypatch.setitem(sys.modules, "django", django_module)
    monkeypatch.setitem(sys.modules, "django.views", django_views)
    monkeypatch.setitem(sys.modules, "django.views.decorators", django_decorators)
    monkeypatch.setitem(sys.modules, "django.views.decorators.csrf", django_csrf)

    ninja_module = types.ModuleType("ninja")

    class Router:
        def __init__(self) -> None:
            self.routes: dict[tuple[str, str], Any] = {}

        def post(self, path: str, **kwargs):  # type: ignore[no-untyped-def]
            return self._register("POST", path)

        def get(self, path: str, **kwargs):  # type: ignore[no-untyped-def]
            return self._register("GET", path)

        def _register(self, method: str, path: str):  # type: ignore[no-untyped-def]
            def decorator(func):  # type: ignore[no-untyped-def]
                self.routes[(method, path)] = func
                return func

            return decorator

    ninja_module.Router = Router
    monkeypatch.setitem(sys.modules, "ninja", ninja_module)


@pytest.fixture
def adapter_module(monkeypatch: pytest.MonkeyPatch):
    _install_django_ninja_stubs(monkeypatch)
    sys.modules.pop("pybotx.presentation.django_ninja", None)
    sys.modules.pop("pybotx.presentation.django_ninja.adapter", None)
    module = importlib.import_module("pybotx.presentation.django_ninja.adapter")

    def _command(bot: DummyBot, payload: dict[str, Any], **kwargs):  # type: ignore[no-untyped-def]
        return bot.async_execute_raw_bot_command(payload, **kwargs)

    async def _smartapp(bot: DummyBot, payload: dict[str, Any], **kwargs):  # type: ignore[no-untyped-def]
        return await bot.sync_execute_raw_smartapp_event(payload, **kwargs)

    async def _status(bot: DummyBot, payload: dict[str, str], **kwargs):  # type: ignore[no-untyped-def]
        return await bot.raw_get_status(payload, **kwargs)

    async def _callback(bot: DummyBot, payload: dict[str, Any], **kwargs):  # type: ignore[no-untyped-def]
        return await bot.set_raw_botx_method_result(payload, **kwargs)

    monkeypatch.setattr(module, "async_execute_raw_bot_command", _command)
    monkeypatch.setattr(module, "sync_execute_raw_smartapp_event", _smartapp)
    monkeypatch.setattr(module, "raw_get_status", _status)
    monkeypatch.setattr(module, "set_raw_botx_method_result", _callback)

    return module


@pytest.mark.asyncio
async def test__django_ninja_adapter__command_success(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/command")]

    status, payload = await handler(DummyRequest(body=b'{"text":"hi"}'))

    assert status == HTTPStatus.ACCEPTED
    assert payload == build_command_accepted_response()
    assert bot.command_payload == {"text": "hi"}


@pytest.mark.asyncio
async def test__django_ninja_adapter__command_validation_error(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/command")]

    status, payload = await handler(DummyRequest(body=b"[]"))

    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload == build_bot_disabled_response("Bot command validation error")


@pytest.mark.asyncio
async def test__django_ninja_adapter__command_unknown_bot(adapter_module) -> None:
    bot = DummyBot()
    bot.command_error = UnknownBotAccountError(
        UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
    )
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/command")]

    status, payload = await handler(DummyRequest(body=b"{}"))

    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload["reason"] == "bot_disabled"


@pytest.mark.asyncio
async def test__django_ninja_adapter__command_unverified(adapter_module) -> None:
    bot = DummyBot()
    bot.command_error = UnverifiedRequestError("invalid")
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/command")]

    status, payload = await handler(DummyRequest(body=b"{}"))

    assert status == HTTPStatus.UNAUTHORIZED
    assert payload == build_unverified_request_response(status_message="invalid")


@pytest.mark.asyncio
async def test__django_ninja_adapter__smartapp_success(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/smartapps/request")]

    status, payload = await handler(DummyRequest(body=b'{"event":"ok"}'))

    assert status == HTTPStatus.OK
    assert payload == {"status": "ok"}
    assert bot.smartapp_payload == {"event": "ok"}


@pytest.mark.asyncio
async def test__django_ninja_adapter__smartapp_unverified(adapter_module) -> None:
    bot = DummyBot()
    bot.smartapp_error = UnverifiedRequestError("bad token")
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/smartapps/request")]

    status, payload = await handler(DummyRequest(body=b"{}"))

    assert status == HTTPStatus.UNAUTHORIZED
    assert payload == build_unverified_request_response(status_message="bad token")


@pytest.mark.asyncio
async def test__django_ninja_adapter__smartapp_validation_error(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/smartapps/request")]

    status, payload = await handler(DummyRequest(body=b"[]"))

    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload == build_bot_disabled_response("Bot command validation error")


@pytest.mark.asyncio
async def test__django_ninja_adapter__smartapp_unknown_bot(adapter_module) -> None:
    bot = DummyBot()
    bot.smartapp_error = UnknownBotAccountError(
        UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
    )
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/smartapps/request")]

    status, payload = await handler(DummyRequest(body=b"{}"))

    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload["reason"] == "bot_disabled"


@pytest.mark.asyncio
async def test__django_ninja_adapter__status_handlers(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    status_handler = adapter.router.routes[("GET", "/status")]
    status_unverified = adapter.router.routes[("GET", "/status__unverified_request")]

    status = await status_handler(DummyRequest(query={"foo": "bar"}))
    assert status == {"status": "ok"}
    assert bot.status_payload == {"foo": "bar"}

    bot.status_error = None
    status_code, payload = await status_unverified(DummyRequest(query={"q": "1"}))
    assert status_code == HTTPStatus.OK
    assert payload == {"status": "ok"}

    bot.status_error = UnverifiedRequestError("missing")
    status_code, payload = await status_unverified(DummyRequest(query={"q": "1"}))
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert payload == build_unverified_request_response(status_message="missing")


@pytest.mark.asyncio
async def test__django_ninja_adapter__callback_and_helpers(adapter_module) -> None:
    bot = DummyBot()
    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/notification/callback")]

    status, payload = await handler(DummyRequest(body=b'{"sync_id":"1"}'))

    assert status == HTTPStatus.ACCEPTED
    assert payload == build_command_accepted_response()
    assert bot.callback_payload == {"sync_id": "1"}

    router = adapter_module.build_django_ninja_router(bot)
    assert hasattr(router, "routes")
    assert adapter_module._parse_json(b"") == {}


@pytest.mark.asyncio
async def test__django_ninja_adapter__command_unmapped_exception(adapter_module) -> None:
    bot = DummyBot()
    bot.command_error = ValueError("boom")

    adapter_module.map_botx_exception = lambda *args, **kwargs: None  # type: ignore[assignment]

    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/command")]

    with pytest.raises(ValueError):
        await handler(DummyRequest(body=b"{}"))


@pytest.mark.asyncio
async def test__django_ninja_adapter__smartapp_unmapped_exception(adapter_module) -> None:
    bot = DummyBot()
    bot.smartapp_error = ValueError("boom")

    adapter_module.map_botx_exception = lambda *args, **kwargs: None  # type: ignore[assignment]

    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("POST", "/smartapps/request")]

    with pytest.raises(ValueError):
        await handler(DummyRequest(body=b"{}"))


@pytest.mark.asyncio
async def test__django_ninja_adapter__status_unverified_unmapped_exception(adapter_module) -> None:
    bot = DummyBot()
    bot.status_error = ValueError("boom")

    adapter_module.map_botx_exception = lambda *args, **kwargs: None  # type: ignore[assignment]

    adapter = adapter_module.DjangoNinjaAdapter(bot)
    handler = adapter.router.routes[("GET", "/status__unverified_request")]

    with pytest.raises(ValueError):
        await handler(DummyRequest(body=b"{}"))
