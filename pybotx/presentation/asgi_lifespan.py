from __future__ import annotations

from collections.abc import Awaitable, Callable

from pybotx.application.bot import Bot


class BotLifespanMiddleware:
    def __init__(self, app: Callable, bot: Bot) -> None:
        self._app = app
        self._bot = bot

    async def __call__(self, scope, receive, send) -> None:  # type: ignore[no-untyped-def]
        if scope["type"] == "lifespan":
            await self._handle_lifespan(receive, send)
            return
        await self._app(scope, receive, send)

    async def _handle_lifespan(
        self,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await self._bot.startup()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await self._bot.shutdown()
                await send({"type": "lifespan.shutdown.complete"})
                return


def wrap_asgi_app(app: Callable, bot: Bot, *, enabled: bool = True) -> Callable:
    if not enabled:
        return app
    return BotLifespanMiddleware(app, bot)
