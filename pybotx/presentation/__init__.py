__all__ = (
    "AiohttpAdapter",
    "DjangoNinjaAdapter",
    "FastAPIAdapter",
    "wrap_asgi_app",
    "build_aiohttp_app",
    "build_django_ninja_router",
    "build_fastapi_router",
)


def __getattr__(name: str):  # type: ignore[override]
    if name in {"AiohttpAdapter", "build_aiohttp_app"}:
        try:
            from pybotx.presentation.aiohttp import AiohttpAdapter, build_aiohttp_app
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "aiohttp integration requires optional dependency `aiohttp`."
            ) from exc

        return {
            "AiohttpAdapter": AiohttpAdapter,
            "build_aiohttp_app": build_aiohttp_app,
        }[name]
    if name in {"DjangoNinjaAdapter", "build_django_ninja_router"}:
        try:
            from pybotx.presentation.django_ninja import (
                DjangoNinjaAdapter,
                build_django_ninja_router,
            )
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "Django Ninja integration requires optional dependencies "
                "`django` and `django-ninja`."
            ) from exc

        return {
            "DjangoNinjaAdapter": DjangoNinjaAdapter,
            "build_django_ninja_router": build_django_ninja_router,
        }[name]
    if name == "wrap_asgi_app":
        from pybotx.presentation.asgi_lifespan import wrap_asgi_app

        return wrap_asgi_app
    if name in {"FastAPIAdapter", "build_fastapi_router"}:
        try:
            from pybotx.presentation.fastapi import FastAPIAdapter, build_fastapi_router
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "FastAPI integration requires optional dependency `fastapi`."
            ) from exc

        return {
            "FastAPIAdapter": FastAPIAdapter,
            "build_fastapi_router": build_fastapi_router,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
