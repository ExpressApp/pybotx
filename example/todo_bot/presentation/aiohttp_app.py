from __future__ import annotations

from aiohttp import web

from pybotx import Bot, AiohttpAdapter


def create_aiohttp_app(bot: Bot, *, verify_requests: bool = True) -> web.Application:
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
