import importlib
import sys
import types
from http import HTTPStatus
from typing import Any

import pytest


class _DummyResponse:
    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
        self.payload = payload
        self.status = status


class _DummyRequest:
    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        headers: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
    ) -> None:
        self._payload = payload or {}
        self.headers = headers or {}
        self.query = query or {}

    async def json(self) -> dict[str, Any]:
        return dict(self._payload)


class _DummyRouter:
    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], Any] = {}

    def add_post(self, path: str, handler: Any) -> None:
        self.routes[("POST", path)] = handler

    def add_get(self, path: str, handler: Any) -> None:
        self.routes[("GET", path)] = handler


class _DummyApplication:
    def __init__(self) -> None:
        self.router = _DummyRouter()
        self.on_startup: list[Any] = []
        self.on_shutdown: list[Any] = []


def _install_aiohttp_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.ModuleType("aiohttp")

    def json_response(payload: dict[str, Any], status: int = 200) -> _DummyResponse:
        return _DummyResponse(payload, status=status)

    web = types.SimpleNamespace(
        Application=_DummyApplication,
        Request=_DummyRequest,
        Response=_DummyResponse,
        json_response=json_response,
    )

    module.web = web
    monkeypatch.setitem(sys.modules, "aiohttp", module)


@pytest.fixture
def adapter_module(monkeypatch: pytest.MonkeyPatch):
    _install_aiohttp_stub(monkeypatch)
    sys.modules.pop("pybotx.presentation.aiohttp", None)
    sys.modules.pop("pybotx.presentation.aiohttp.adapter", None)
    module = importlib.import_module("pybotx.presentation.aiohttp.adapter")
    return module


@pytest.mark.asyncio
async def test__aiohttp_adapter__handlers_success(adapter_module) -> None:
    called: dict[str, Any] = {}

    def _command(bot, payload, **kwargs):  # type: ignore[no-untyped-def]
        called["command"] = payload

    async def _smartapp(bot, payload, **kwargs):  # type: ignore[no-untyped-def]
        called["smartapp"] = payload

        class _Resp:
            def jsonable_dict(self) -> dict[str, Any]:
                return {"status": "ok"}

        return _Resp()

    async def _status(bot, query, **kwargs):  # type: ignore[no-untyped-def]
        called.setdefault("status", []).append(query)
        return {"status": "ok"}

    async def _callback(bot, payload, **kwargs):  # type: ignore[no-untyped-def]
        called["callback"] = payload

    adapter_module.async_execute_raw_bot_command = _command
    adapter_module.sync_execute_raw_smartapp_event = _smartapp
    adapter_module.raw_get_status = _status
    adapter_module.set_raw_botx_method_result = _callback
    adapter_module.build_command_accepted_response = lambda: {"accepted": True}
    adapter_module.map_botx_exception = lambda *args, **kwargs: (  # type: ignore[assignment]
        HTTPStatus.BAD_REQUEST,
        {"error": "bad"},
    )

    adapter = adapter_module.AiohttpAdapter(object())

    command_response = await adapter._command_handler(
        _DummyRequest({"text": "hi"}, headers={"x": "y"})
    )
    assert command_response.status == HTTPStatus.ACCEPTED
    assert command_response.payload == {"accepted": True}

    smartapp_response = await adapter._smartapp_handler(_DummyRequest({"k": "v"}))
    assert smartapp_response.status == HTTPStatus.OK
    assert smartapp_response.payload == {"status": "ok"}

    status_response = await adapter._status_handler(
        _DummyRequest(query={"ready": "1"})
    )
    assert status_response.payload == {"status": "ok"}

    status_unverified_response = await adapter._status_handler_unverified(
        _DummyRequest(query={"ready": "2"})
    )
    assert status_unverified_response.payload == {"status": "ok"}

    callback_response = await adapter._callback_handler(_DummyRequest({"id": "1"}))
    assert callback_response.status == HTTPStatus.ACCEPTED

    assert called["command"] == {"text": "hi"}
    assert called["smartapp"] == {"k": "v"}
    assert called["status"] == [{"ready": "1"}, {"ready": "2"}]
    assert called["callback"] == {"id": "1"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler_name, raise_func",
    [
        ("_command_handler", "async_execute_raw_bot_command"),
        ("_smartapp_handler", "sync_execute_raw_smartapp_event"),
        ("_status_handler_unverified", "raw_get_status"),
    ],
)
async def test__aiohttp_adapter__handlers_map_error(
    adapter_module,
    handler_name: str,
    raise_func: str,
) -> None:
    def _raise(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    async def _raise_async(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    if raise_func == "async_execute_raw_bot_command":
        adapter_module.async_execute_raw_bot_command = _raise
    elif raise_func == "sync_execute_raw_smartapp_event":
        adapter_module.sync_execute_raw_smartapp_event = _raise_async
    else:
        adapter_module.raw_get_status = _raise_async

    adapter_module.map_botx_exception = lambda *args, **kwargs: (  # type: ignore[assignment]
        HTTPStatus.BAD_REQUEST,
        {"error": "bad"},
    )

    adapter = adapter_module.AiohttpAdapter(object())
    handler = getattr(adapter, handler_name)

    response = await handler(_DummyRequest())

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.payload == {"error": "bad"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler_name, raise_func",
    [
        ("_command_handler", "async_execute_raw_bot_command"),
        ("_smartapp_handler", "sync_execute_raw_smartapp_event"),
        ("_status_handler_unverified", "raw_get_status"),
    ],
)
async def test__aiohttp_adapter__handlers_raise_unmapped(
    adapter_module,
    handler_name: str,
    raise_func: str,
) -> None:
    def _raise(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    async def _raise_async(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    if raise_func == "async_execute_raw_bot_command":
        adapter_module.async_execute_raw_bot_command = _raise
    elif raise_func == "sync_execute_raw_smartapp_event":
        adapter_module.sync_execute_raw_smartapp_event = _raise_async
    else:
        adapter_module.raw_get_status = _raise_async

    adapter_module.map_botx_exception = lambda *args, **kwargs: None  # type: ignore[assignment]

    adapter = adapter_module.AiohttpAdapter(object())
    handler = getattr(adapter, handler_name)

    with pytest.raises(ValueError):
        await handler(_DummyRequest())


@pytest.mark.asyncio
async def test__build_aiohttp_app__startup_shutdown(adapter_module) -> None:
    class _Bot:
        def __init__(self) -> None:
            self.started = 0
            self.stopped = 0

        async def startup(self) -> None:
            self.started += 1

        async def shutdown(self) -> None:
            self.stopped += 1

    bot = _Bot()
    app = adapter_module.build_aiohttp_app(bot)

    assert len(app.on_startup) == 1
    assert len(app.on_shutdown) == 1

    await app.on_startup[0](app)
    await app.on_shutdown[0](app)

    assert bot.started == 1
    assert bot.stopped == 1

    aiohttp_module = importlib.import_module("pybotx.presentation.aiohttp")
    assert hasattr(aiohttp_module, "AiohttpAdapter")
    assert hasattr(aiohttp_module, "build_aiohttp_app")
