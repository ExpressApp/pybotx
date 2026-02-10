from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI

from pybotx import Bot, wrap_asgi_app
from pybotx.presentation.fastapi import FastAPIAdapter


def create_app(
    bot: Bot,
    *,
    verify_requests: bool = True,
    use_lifespan_wrapper: bool = True,
) -> Callable:
    adapter = FastAPIAdapter(bot, verify_requests=verify_requests)
    app = FastAPI(title="Todo Bot")
    app.include_router(adapter.router)
    if use_lifespan_wrapper:
        return wrap_asgi_app(app, bot)
    app.add_event_handler("startup", bot.startup)
    app.add_event_handler("shutdown", bot.shutdown)
    return app
