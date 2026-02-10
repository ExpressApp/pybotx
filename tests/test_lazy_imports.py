import importlib
import sys
import types

import pytest


def _install_fastapi_stub(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("pybotx.presentation.fastapi")

    class StubAdapter:
        pass

    def build_router() -> str:
        return "router"

    module.FastAPIAdapter = StubAdapter
    module.build_fastapi_router = build_router

    monkeypatch.setitem(sys.modules, "pybotx.presentation.fastapi", module)
    return module


def _install_aiohttp_stub(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("pybotx.presentation.aiohttp")

    class StubAdapter:
        pass

    def build_app() -> str:
        return "app"

    module.AiohttpAdapter = StubAdapter
    module.build_aiohttp_app = build_app

    monkeypatch.setitem(sys.modules, "pybotx.presentation.aiohttp", module)
    return module


def _install_django_ninja_stub(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("pybotx.presentation.django_ninja")

    class StubAdapter:
        pass

    def build_router() -> str:
        return "router"

    module.DjangoNinjaAdapter = StubAdapter
    module.build_django_ninja_router = build_router

    monkeypatch.setitem(sys.modules, "pybotx.presentation.django_ninja", module)
    return module


def test__lazy_imports__aiohttp_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import pybotx
    import pybotx.presentation as presentation

    stub = _install_aiohttp_stub(monkeypatch)

    assert pybotx.AiohttpAdapter is stub.AiohttpAdapter
    assert pybotx.build_aiohttp_app is stub.build_aiohttp_app

    assert presentation.AiohttpAdapter is stub.AiohttpAdapter
    assert presentation.build_aiohttp_app is stub.build_aiohttp_app


def test__lazy_imports__aiohttp_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pybotx
    import pybotx.presentation as presentation

    monkeypatch.delitem(sys.modules, "pybotx.presentation.aiohttp", raising=False)

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[override]
        if name == "pybotx.presentation.aiohttp":
            raise ModuleNotFoundError("No module named 'aiohttp'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ModuleNotFoundError):
        _ = pybotx.AiohttpAdapter

    with pytest.raises(ModuleNotFoundError):
        _ = presentation.AiohttpAdapter


def test__lazy_imports__django_ninja_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import pybotx
    import pybotx.presentation as presentation

    stub = _install_django_ninja_stub(monkeypatch)

    assert pybotx.DjangoNinjaAdapter is stub.DjangoNinjaAdapter
    assert pybotx.build_django_ninja_router is stub.build_django_ninja_router

    assert presentation.DjangoNinjaAdapter is stub.DjangoNinjaAdapter
    assert presentation.build_django_ninja_router is stub.build_django_ninja_router


def test__lazy_imports__django_ninja_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pybotx
    import pybotx.presentation as presentation

    monkeypatch.delitem(sys.modules, "pybotx.presentation.django_ninja", raising=False)

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[override]
        if name == "pybotx.presentation.django_ninja":
            raise ModuleNotFoundError("No module named 'django'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ModuleNotFoundError):
        _ = pybotx.DjangoNinjaAdapter

    with pytest.raises(ModuleNotFoundError):
        _ = presentation.DjangoNinjaAdapter


def test__lazy_imports__fastapi_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import pybotx
    import pybotx.presentation as presentation

    stub = _install_fastapi_stub(monkeypatch)

    assert pybotx.FastAPIAdapter is stub.FastAPIAdapter
    assert pybotx.build_fastapi_router is stub.build_fastapi_router

    assert presentation.FastAPIAdapter is stub.FastAPIAdapter
    assert presentation.build_fastapi_router is stub.build_fastapi_router


def test__lazy_imports__fastapi_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pybotx
    import pybotx.presentation as presentation

    monkeypatch.delitem(sys.modules, "pybotx.presentation.fastapi", raising=False)

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[override]
        if name == "pybotx.presentation.fastapi":
            raise ModuleNotFoundError("No module named 'fastapi'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ModuleNotFoundError):
        _ = pybotx.FastAPIAdapter

    with pytest.raises(ModuleNotFoundError):
        _ = presentation.FastAPIAdapter


def test__lazy_imports__domain_submodule() -> None:
    import pybotx.domain as domain
    constants_module = importlib.import_module("pybotx.domain.constants")
    if hasattr(domain, "constants"):
        delattr(domain, "constants")

    assert domain.constants is constants_module

    with pytest.raises(AttributeError):
        _ = domain.not_existing


def test__lazy_imports__unknown_attribute() -> None:
    import pybotx
    import pybotx.presentation as presentation

    with pytest.raises(AttributeError):
        _ = pybotx.not_existing

    with pytest.raises(AttributeError):
        _ = presentation.not_existing


def test__application_contextvars_reexport() -> None:
    from pybotx.application import contextvars as app_contextvars
    from pybotx.domain import contextvars as domain_contextvars

    assert app_contextvars.bot_var is domain_contextvars.bot_var
    assert app_contextvars.bot_id_var is domain_contextvars.bot_id_var
    assert app_contextvars.chat_id_var is domain_contextvars.chat_id_var


def test__ports_lazy_exports() -> None:
    import pybotx.domain.ports as ports
    from pybotx.domain.ports import async_buffer as async_buffer_module
    from pybotx.domain.ports import bot_access as bot_access_module
    from pybotx.domain.ports import bot_accounts_storage as bot_accounts_storage_module
    from pybotx.domain.ports import botx_api as botx_api_module
    from pybotx.domain.ports import callback_manager as callback_manager_module
    from pybotx.domain.ports import callback_repo as callback_repo_module
    from pybotx.domain.ports import dedup_store as dedup_store_module
    from pybotx.domain.ports import http_client as http_client_module
    from pybotx.domain.ports import jwt_encoder as jwt_encoder_module
    from pybotx.domain.ports import jwt_verifier as jwt_verifier_module
    from pybotx.domain.ports import retry_policy as retry_policy_module

    assert ports.AsyncBufferBase is async_buffer_module.AsyncBufferBase
    assert ports.AsyncBufferReadable is async_buffer_module.AsyncBufferReadable
    assert ports.AsyncBufferWritable is async_buffer_module.AsyncBufferWritable
    assert ports.get_file_size is async_buffer_module.get_file_size
    assert ports.BotAccessPort is bot_access_module.BotAccessPort
    assert ports.BotAccountsStoragePort is bot_accounts_storage_module.BotAccountsStoragePort
    assert ports.BotXApiPort is botx_api_module.BotXApiPort
    assert ports.CallbackManagerPort is callback_manager_module.CallbackManagerPort
    assert ports.CallbackRepoProto is callback_repo_module.CallbackRepoProto
    assert ports.DedupStorePort is dedup_store_module.DedupStorePort
    assert ports.HttpClientPort is http_client_module.HttpClientPort
    assert ports.HttpRequest is http_client_module.HttpRequest
    assert ports.HttpResponse is http_client_module.HttpResponse
    assert ports.HttpClientError is http_client_module.HttpClientError
    assert ports.HttpTransportError is http_client_module.HttpTransportError
    assert ports.HttpTimeoutError is http_client_module.HttpTimeoutError
    assert ports.HttpStatusError is http_client_module.HttpStatusError
    assert ports.JwtEncoderPort is jwt_encoder_module.JwtEncoderPort
    assert ports.JwtVerifierPort is jwt_verifier_module.JwtVerifierPort
    assert ports.RetryPolicyPort is retry_policy_module.RetryPolicyPort

    with pytest.raises(AttributeError):
        _ = ports.not_existing


def test__lazy_imports__wrap_asgi_app() -> None:
    import pybotx
    import pybotx.presentation as presentation
    from pybotx.presentation.asgi_lifespan import wrap_asgi_app

    assert pybotx.wrap_asgi_app is wrap_asgi_app
    assert presentation.wrap_asgi_app is wrap_asgi_app


def test__exceptions_reexports() -> None:
    from pybotx.domain.errors import (
        SyncSmartAppEventHandlerNotFoundError,
        UnknownSystemEventError,
        UnsupportedBotAPIVersionError,
    )
    from pybotx.infrastructure.client.smartapps_api import exceptions as smartapp_exceptions
    from pybotx.presentation.api import exceptions as presentation_exceptions

    assert (
        smartapp_exceptions.SyncSmartAppEventHandlerNotFoundError
        is SyncSmartAppEventHandlerNotFoundError
    )
    assert presentation_exceptions.UnknownSystemEventError is UnknownSystemEventError
    assert (
        presentation_exceptions.UnsupportedBotAPIVersionError
        is UnsupportedBotAPIVersionError
    )


def test__bot__compat_attributes_not_set_for_custom_botx_api() -> None:
    from pybotx.application.bot import Bot
    from pybotx.application.callbacks.callback_manager import CallbackManager
    from pybotx.application.request_verifier import RequestVerifier
    from pybotx.infrastructure.auth import BotXAuthVersion
    from pybotx.infrastructure.bot_accounts_storage import BotAccountsStorage
    from pybotx.infrastructure.jwt_encoder import PyJwtEncoder
    from pybotx.infrastructure.callbacks.callback_memory_repo import CallbackMemoryRepo
    from pybotx.infrastructure.jwt_verifier import PyJwtVerifier

    class DummyBotXApi:
        pass

    bot_accounts_storage = BotAccountsStorage(
        [],
        BotXAuthVersion.V2,
        jwt_encoder=PyJwtEncoder(),
    )
    bot = Bot(
        collectors=[],
        bot_accounts_storage=bot_accounts_storage,
        callbacks_manager=CallbackManager(CallbackMemoryRepo()),
        botx_api=DummyBotXApi(),
        request_verifier=RequestVerifier(
            bot_accounts_storage=bot_accounts_storage,
            jwt_verifier=PyJwtVerifier(),
        ),
    )

    assert not hasattr(bot, "_http_client")
    assert not hasattr(bot, "_default_callback_timeout")
